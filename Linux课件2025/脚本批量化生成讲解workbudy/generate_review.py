# -*- coding: utf-8 -*-
"""
generate_review.py — 聊天版讲解稿 → 复习版（长期复习用）

用法：
    python generate_review.py <聊天版.md> [课件骨架.md] [输出文件名.md] [--depth 2]

说明：
    1. 同目录下需有 config.json（base_url / api_key / model）和 review_system_prompt.txt
    2. 若提供"课件骨架"文件（如目录汇总对应章节），脚本提取其中标题作为骨架注入；
       --depth N 控制保留到第几级标题（默认 2，即只保留 # 和 ##，保证复习版标题极少）
    3. 输出默认：<聊天版文件名>-复习版.md，保存在与聊天版同目录
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


def load_system_prompt():
    with open(os.path.join(BASE_DIR, "review_system_prompt.txt"), encoding="utf-8") as f:
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


def main():
    argv = [a for a in sys.argv[1:] if a != "--depth"]
    depth = 2
    for i, a in enumerate(sys.argv):
        if a == "--depth" and i + 1 < len(sys.argv):
            depth = int(sys.argv[i + 1])
    # 去掉 --depth 及其取值，剩下的位置参数依次为：源文件 / 骨架 / 输出名
    if "--depth" in sys.argv:
        idx = sys.argv.index("--depth")
        argv = sys.argv[1:idx] + sys.argv[idx + 2:]

    if not argv:
        sys.exit("用法：python generate_review.py <聊天版.md> [课件骨架.md] [输出文件名.md] [--depth 2]")

    src_path = argv[0]
    with open(src_path, encoding="utf-8") as f:
        source = f.read()

    outline_block = ""
    if len(argv) >= 2:
        with open(argv[1], encoding="utf-8") as f:
            outline = extract_outline(f.read(), depth)
        if outline.strip():
            outline_block = (
                "\n\n【精简骨架——复习版的标题只能使用下面这些标题：原样照抄，"
                "不得增加、删除、改写，也不得再出现任何三级及以下标题】\n" + outline
            )
            print("已加载精简骨架（保留 %d 级以内，共 %d 个标题）。"
                  % (depth, len(outline.split("\n"))))

    url, key, model = load_config()
    system_prompt = load_system_prompt()

    user_content = (
        "请把下面这份讲解稿（聊天版）压缩成一份复习版。"
        "目标是：读者很久以后只看复习版，就能回忆起本节大部分内容。\n"
        "以下两部分是顺序无关的并列材料：\n\n"
        "===== 讲解稿（内容来源）=====\n" + source + outline_block
    )

    if len(argv) >= 3:
        out_name = argv[2]
    else:
        out_name = os.path.splitext(os.path.basename(src_path))[0] + "-复习版.md"
    out_path = os.path.join(os.path.dirname(os.path.abspath(src_path)), out_name)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    print("正在生成复习版（模型：%s）……" % model)
    full, finish = chat(url, key, model, messages)
    with open(out_path, "w", encoding="utf-8") as f:  # 先落盘，避免中途失败丢结果
        f.write(full)

    rounds = 0
    while finish == "length" and rounds < MAX_CONTINUE:
        rounds += 1
        print("输出被截断，自动发送「继续」补全（第 %d 轮）……" % rounds)
        messages.append({"role": "assistant", "content": full})
        messages.append({"role": "user", "content": "继续"})
        part, finish = chat(url, key, model, messages)
        full += "\n" + part
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full)

    print("完成：%s（%d 字符）" % (out_path, len(full)))


if __name__ == "__main__":
    main()
