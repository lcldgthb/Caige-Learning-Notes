# -*- coding: utf-8 -*-
"""
generate_lecture.py — 大纲/内容提要 → 聊天版讲解稿（中转站 OpenAI 兼容 API）

用法：
    python generate_lecture.py <大纲或提要.md> [输出文件名.md]

说明：
    1. 同目录下需有 config.json（base_url / api_key / model）和 system_prompt.txt
    2. 不指定输出文件名时，自动取输入文件第一个 # 标题 + "聊天版.md"
    3. 输出保存在脚本所在目录
    4. 若模型单次输出被截断，脚本会自动发送"继续"补全（最多 5 轮）
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
TIMEOUT = 300


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
    with open(os.path.join(BASE_DIR, "system_prompt.txt"), encoding="utf-8") as f:
        return f.read()


def load_learned_block():
    """同目录下若存在 已学记录.md 且有内容，生成注入用户消息的已学清单块。"""
    path = os.path.join(BASE_DIR, "已学记录.md")
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        learned = f.read().strip()
    if not learned:
        return ""
    return (
        "\n\n【已学清单——以下内容读者已经掌握，禁止展开讲解，最多半句话提及名称或直接跳过；"
        "仅当新旧知识有天然联系时可用一句话点出关联】\n" + learned
    )


def chat(url, key, model, messages):
    """流式调用（SSE），避免长输出时网关 524 超时。返回 (完整文本, finish_reason)。"""
    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 8000,
        "stream": True,
    }).encode("utf-8")
    req = urllib.request.Request(
        url + "/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + key,
            "Accept": "text/event-stream",
        },
    )
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
            # 5xx（如 524 源站超时）重试；4xx（如 401 key 错误）直接退出
            if e.code < 500:
                sys.exit("API 请求失败 HTTP %s：%s" % (e.code, e.read().decode("utf-8", "ignore")[:500]))
            print("HTTP %d，%d 秒后重试（第 %d/%d 次）……" % (e.code, 10 * attempt, attempt, MAX_RETRY))
            time.sleep(10 * attempt)
        except Exception as e:
            last_err = e
            print("请求异常：%s，%d 秒后重试（第 %d/%d 次）……" % (e, 10 * attempt, attempt, MAX_RETRY))
            time.sleep(10 * attempt)
    sys.exit("API 请求连续失败 %d 次，最后错误：%s" % (MAX_RETRY, last_err))


def derive_output_name(input_text, input_path):
    m = re.search(r"^#\s+(.+)$", input_text, re.MULTILINE)
    title = m.group(1).strip() if m else os.path.splitext(os.path.basename(input_path))[0]
    title = re.sub(r'[\\/:*?"<>|]', "_", title)
    return title + "聊天版.md"


def split_sections(text):
    """按 ## 大节切分提要，返回 (大标题, [各节文本])。无法切分时返回单节列表。"""
    title_m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else ""
    chunks = []
    cur = None
    for ln in text.split("\n"):
        if ln.startswith("## "):
            if cur is not None:
                chunks.append("\n".join(cur).strip())
            cur = [ln]
        elif cur is not None:
            cur.append(ln)
    if cur is not None:
        chunks.append("\n".join(cur).strip())
    chunks = [c for c in chunks if c]
    return title, chunks


def generate_one(url, key, model, system_prompt, user_content):
    """单次生成（含截断自动继续）。"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    full, finish = chat(url, key, model, messages)
    rounds = 0
    while finish == "length" and rounds < MAX_CONTINUE:
        rounds += 1
        print("  输出被截断，自动发送「继续」补全（第 %d 轮）……" % rounds)
        messages.append({"role": "assistant", "content": full})
        messages.append({"role": "user", "content": "继续"})
        part, finish = chat(url, key, model, messages)
        full += "\n" + part
    return full


def main():
    if len(sys.argv) < 2:
        sys.exit("用法：python generate_lecture.py <大纲或提要.md> [输出文件名.md]")

    input_path = sys.argv[1]
    with open(input_path, encoding="utf-8") as f:
        material = f.read()

    url, key, model = load_config()
    system_prompt = load_system_prompt()
    learned_block = load_learned_block()
    if learned_block:
        print("已加载 已学记录.md，已学内容将被跳过。")

    title, chunks = split_sections(material)
    parts = []

    if len(chunks) > 1:
        print("检测到 %d 个大节，分节生成（模型：%s）……" % (len(chunks), model))
        for i, chunk in enumerate(chunks, 1):
            first_line = chunk.split("\n", 1)[0]
            print("[%d/%d] 生成 %s ……" % (i, len(chunks), first_line))
            user_content = "这是课程《%s》第 %d/%d 节的内容提要，请按照提要对这一节进行零基础讲解：\n\n%s" % (
                title, i, len(chunks), chunk)
            parts.append(generate_one(url, key, model, system_prompt, user_content + learned_block))
    else:
        print("正在生成（模型：%s）……" % model)
        user_content = "请按照以下内容提要/大纲，对这节课进行零基础讲解：\n\n" + material
        parts.append(generate_one(url, key, model, system_prompt, user_content + learned_block))

    full = ("\n\n---\n\n").join(parts)

    out_name = sys.argv[2] if len(sys.argv) >= 3 else derive_output_name(material, input_path)
    out_path = os.path.join(BASE_DIR, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full)

    print("完成：%s（%d 字符）" % (out_path, len(full)))


if __name__ == "__main__":
    main()
