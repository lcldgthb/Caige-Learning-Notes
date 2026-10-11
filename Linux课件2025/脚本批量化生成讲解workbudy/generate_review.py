# -*- coding: utf-8 -*-
"""
generate_review.py — 讲解稿/课件 markdown → 复习版（长期复习用）

用法一（多源整合，推荐）：
    python generate_review.py --sources <源1.md> <源2.md> ... --outline <骨架.md> --output <输出名.md> [--depth 2]

用法二（旧式单源，向后兼容）：
    python generate_review.py <聊天版.md> [课件骨架.md] [输出文件名.md] [--depth 2]

说明：
    1. 同目录下需有 config.json（base_url / api_key / model）和 review_system_prompt.txt
    2. --sources 可指定多份并列材料（如 聊天版 + PDF课件markdown），按给定顺序拼接注入
    3. --outline 提取骨架标题注入，--depth N 控制保留到第几级标题（默认 2，保证标题极少）
    4. 输出被截断时自动发送「继续」补全（最多 5 轮）
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_CONTINUE = 5
MAX_RETRY = 3
TIMEOUT = 600
MAX_TOKENS = 16000


def load_config():
    with open(os.path.join(BASE_DIR, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    base = cfg["base_url"].strip().rstrip("/")
    if not base.endswith("/v1"):
        base += "/v1"
    if not cfg["api_key"] or "在这里填" in cfg["api_key"]:
        sys.exit("请先在 config.json 里填写 api_key")
    return base, cfg["api_key"], cfg["model"]


def load_system_prompt(prompt_file="review_system_prompt.txt"):
    with open(os.path.join(BASE_DIR, prompt_file), encoding="utf-8") as f:
        return f.read()


def extract_outline(text, depth=2):
    """提取 markdown 标题行作为骨架，只保留层级 <= depth 的标题。"""
    lines = []
    for ln in text.split("\n"):
        m = re.match(r"^(#{1,6})\s+\S", ln)
        if m and len(m.group(1)) <= depth:
            lines.append(ln.rstrip())
    return "\n".join(lines)


def chat(url, key, model, messages):
    """流式调用（SSE），避免长输出时网关超时。返回 (完整文本, finish_reason)。"""
    body = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "stream": True,
    }).encode("utf-8")

    def build_req(target):
        return urllib.request.Request(
            target,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + key,
                "Accept": "text/event-stream",
            },
        )

    req = build_req(url + "/chat/completions")
    last_err = None
    for attempt in range(1, MAX_RETRY + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                content_parts = []
                finish_reason = ""
                for raw in resp:
                    line = raw.decode("utf-8", "ignore").strip()
                    if not line.startswith("data:"):
                        continue
                    payload = line[5:].strip()
                    if payload == "[DONE]":
                        break
                    try:
                        chunk = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    for choice in chunk.get("choices", []):
                        delta = choice.get("delta", {})
                        if delta.get("content"):
                            content_parts.append(delta["content"])
                        if choice.get("finish_reason"):
                            finish_reason = choice["finish_reason"]
                if not content_parts:
                    raise RuntimeError("流式响应为空")
                return "".join(content_parts), finish_reason
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (301, 302, 307, 308):
                loc = e.headers.get("Location")
                if loc:
                    print("HTTP %d 重定向，跟随 Location 继续请求……" % e.code)
                    req = build_req(loc)
                    attempt -= 1
                    continue
            if e.code != 429 and e.code < 500:
                sys.exit("API 请求失败 HTTP %s：%s" % (e.code, e.read().decode("utf-8", "ignore")[:500]))
            wait = 20 * attempt if e.code == 429 else 10 * attempt
            print("HTTP %d，%d 秒后重试（第 %d/%d 次）……" % (e.code, wait, attempt, MAX_RETRY))
            time.sleep(wait)
        except Exception as e:
            last_err = e
            print("请求异常：%s，%d 秒后重试（第 %d/%d 次）……" % (e, 10 * attempt, attempt, MAX_RETRY))
            time.sleep(10 * attempt)
    sys.exit("API 请求连续失败 %d 次，最后错误：%s" % (MAX_RETRY, last_err))


def parse_args():
    """解析命令行。支持 --sources/--outline/--output/--depth 标志和旧式位置参数。"""
    args = sys.argv[1:]
    depth = 2
    sources, outline_path, out_name = [], None, None

    # 提取 --depth N
    if "--depth" in args:
        i = args.index("--depth")
        if i + 1 >= len(args):
            sys.exit("--depth 需要一个数值参数")
        depth = int(args[i + 1])
        args = args[:i] + args[i + 2:]

    def take_values(flag):
        """收集 flag 后面连续的非标志参数，返回 (取值列表, 移除后的剩余参数)。"""
        if flag not in args:
            return [], args
        i = args.index(flag)
        vals = []
        j = i + 1
        while j < len(args) and not args[j].startswith("--"):
            vals.append(args[j])
            j += 1
        return vals, args[:i] + args[j:]

    sources, args = take_values("--sources")
    if "--outline" in args:
        i = args.index("--outline")
        outline_path = args[i + 1]
        args = args[:i] + args[i + 2:]
    if "--output" in args:
        i = args.index("--output")
        out_name = args[i + 1]
        args = args[:i] + args[i + 2:]

    # 标志模式：--sources 必须给了
    if sources:
        if not outline_path or not out_name:
            sys.exit("标志模式需要同时提供 --sources / --outline / --output")
        return sources, outline_path, out_name, depth

    # 旧式位置参数：源文件 / 骨架 / 输出名
    if not args:
        sys.exit("用法：python generate_review.py --sources <源1.md> <源2.md> --outline <骨架.md> --output <输出名.md> [--depth 2]\n"
                 "      或：python generate_review.py <聊天版.md> [课件骨架.md] [输出文件名.md] [--depth 2]")
    sources = [args[0]]
    outline_path = args[1] if len(args) >= 2 else None
    out_name = args[2] if len(args) >= 3 else None
    return sources, outline_path, out_name, depth


def main():
    sources, outline_path, out_name, depth = parse_args()

    # --prompt 选择系统提示词文件（默认 review_system_prompt.txt，博客版用 blog_system_prompt.txt）
    prompt_file = "review_system_prompt.txt"
    if "--prompt" in sys.argv:
        i = sys.argv.index("--prompt")
        prompt_file = sys.argv[i + 1]
        if i + 1 >= len(sys.argv):
            sys.exit("--prompt 需要一个文件名参数")

    source_blocks = []
    n_labels = ["材料一（PDF课件原文）", "材料二（讲解稿/聊天版）", "材料三", "材料四", "材料五"]
    for idx, sp in enumerate(sources):
        with open(sp, encoding="utf-8") as f:
            source_blocks.append("===== %s：%s =====\n%s" % (
                n_labels[idx] if idx < len(n_labels) else "材料%d" % (idx + 1),
                os.path.basename(sp),
                f.read()))
    source = "\n\n".join(source_blocks)

    outline_block = ""
    if outline_path:
        with open(outline_path, encoding="utf-8") as f:
            outline = extract_outline(f.read(), depth)
        if outline.strip():
            outline_block = (
                "\n\n【精简骨架——复习版的标题只能使用下面这些标题：原样照抄，"
                "不得增加、删除、改写，也不得再出现任何三级及以下标题】\n" + outline
            )
            print("已加载精简骨架（保留 %d 级以内，共 %d 个标题）。"
                  % (depth, len(outline.split("\n"))))

    url, key, model = load_config()
    system_prompt = load_system_prompt(prompt_file)

    user_content = (
        "请把下面的材料整合压缩成一份复习版（博客版）。"
        "目标是：读者很久以后只看这份复习版，就能回忆起本节大部分内容。\n"
        "多份材料内容互有重叠，请提炼合并，不要逐份重复；"
        "讲解稿里的类比与展开可删，但课件中的命令、函数原型、参数、返回值、"
        "易错点等硬知识一条都不能丢。\n\n" + source + outline_block
    )

    if out_name:
        out_path = os.path.join(os.path.dirname(os.path.abspath(sources[0])), out_name)
    else:
        out_path = os.path.splitext(os.path.abspath(sources[0]))[0] + "-复习版.md"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    print("正在生成复习版（模型：%s，输入 %d 份材料，共 %d 字符）……"
          % (model, len(sources), len(user_content)))
    full, finish = chat(url, key, model, messages)
    with open(out_path, "w", encoding="utf-8") as f:  # 先落盘，避免中途失败丢结果
        f.write(full)

    rounds = 0
    # finish_reason 为空说明流中途断开（非正常 stop），同样需要续写补全
    while finish in ("length", "") and rounds < MAX_CONTINUE:
        rounds += 1
        if finish == "length":
            print("输出被截断，自动发送「继续」补全（第 %d 轮）……" % rounds)
        else:
            print("流式响应异常中断（finish_reason 为空），自动发送「继续」补全（第 %d 轮）……" % rounds)
        messages.append({"role": "assistant", "content": full})
        messages.append({"role": "user", "content": "继续"})
        part, finish = chat(url, key, model, messages)
        full += "\n" + part
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full)

    print("完成：%s（%d 字符）" % (out_path, len(full)))


if __name__ == "__main__":
    main()
