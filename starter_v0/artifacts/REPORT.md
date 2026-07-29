# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 11:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team: G16 (E403)
- Members: Phan Trong Tien (01095) + teammates
- Provider/model: openrouter / `openai/gpt-4o-mini`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent: tìm tin web/Twitter theo từ khóa hoặc tài khoản, đọc URL, hỏi lại khi thiếu thông tin, xác nhận trước khi gửi Telegram, và (tool mới) xếp hạng item theo độ liên quan.

**Link dùng thử (truy cập được trong showdown):**

> URL: `http://localhost:8501` (Streamlit). Trước showdown chạy `streamlit run app.py` rồi (nếu cần máy khác) `cloudflared tunnel --url http://localhost:8501` và dán link `trycloudflare.com` vào đây.
>
> URL public (điền khi tunnel sống):

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại khi thiếu info / confirm yes-no trước send | không |
| timeline | tweet gần đây của 1 handle | không |
| social_search | tìm tweet theo từ khóa | không |
| lookup | tìm trên web (news/general + timeframe) | không |
| fetch | đọc nội dung 1 URL | không |
| format | render digest markdown từ items | không |
| rank | xếp hạng items đã có theo query (local) | **có** |
| send | gửi Telegram (cần confirm) | không (optional) |
| policy / papers / paper_text | optional built-ins | không |

## A3. Câu hỏi mẫu để thử

1. `Tweet mới nhất của Sam Altman là gì?`
2. `Tin AI hôm nay có gì nổi bật?`
3. `Tóm tắt bài viết này hộ mình` (thiếu URL → expect clarify)
4. `Đăng bản tin này lên Telegram giúp mình` (expect clarify yes/no)
5. `Tìm trên web tin AI hôm nay và tìm thêm tweet về AI.`

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Thiếu handle | `clarify(response_type=text)` | v0 đoán `sama`; v1+ hỏi lại | `transcripts/..._live_clarify.transcript.json` |
| Confirm send | `clarify(response_type=yes_no)` | v0 gọi `send`; v2+ boundary đúng | `transcripts/..._live_boundary.transcript.json` |
| Web news | `lookup(topic=news,timeframe=day)` | routing ổn từ early versions | `transcripts/..._live_research.transcript.json` |
| Out of scope | no tool | v0 gửi qua `send`; v1+ refuse | `runs/v0_...` vs `runs/v3_...` R08/R14 |
| Drop Twitter → web | chỉ `lookup` | v3 harden YAML + latest-turn rule | base M06 + group G10 |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline starter prompt | Đo hành vi đoán/gửi bừa | case_accuracy |  | 0.70 | `runs/v0_B_base_openrouter_01095_PHANTRONGTIEN.json` |
| v1 | `system_prompt.md`: clarify / confirm / OOS refuse | Missing-info + boundary fail vì prompt cấm hỏi lại | case_accuracy | 0.70 | 0.90 | `runs/v1_B_base_openrouter_01095_PHANTRONGTIEN.json` |
| v2 | prompt: map famous names; send → yes_no | R01 over-clarify; R12 dùng text thay yes_no | case_accuracy | 0.90 | 1.00 | `runs/v2_B_base_openrouter_01095_PHANTRONGTIEN.json` |
| v3 | harden `tools.yaml` (+ latest-turn drop-Twitter) | Declaration mơ hồ + parallel hint gây regression M06 | case_accuracy | 1.00 | 1.00 | `runs/v3_B_base_openrouter_01095_PHANTRONGTIEN.json` |

Group suite @ v3: **10/10**, `runs/v3_B_group_openrouter_01095_PHANTRONGTIEN.json`.

## B2. Failure analysis

Use actual failures from `results[*].result.failures` (chủ yếu từ v0; v1 còn 2; v2/v3 sạch base).

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08 / R14 | out_of_scope | `send(...)` | unexpected_tool_call | v1: refuse OOS, no tool |
| R10 | missing_info | `timeline(sama)` | missing clarify | v1: không đoán handle |
| R11 | missing_info | `fetch(fake url)` | missing clarify | v1: hỏi URL |
| R12 | wrong_boundary | `send` / later `clarify(text)` | thiếu yes_no | v1–v2: clarify yes_no trước send |
| R13 | wrong_arg_value | lookup query/topic lệch | args | v1+ convention news args |
| R01 (v1) | wrong_tool | `clarify` thay `timeline` | over-clarify tên nổi tiếng | v2: map name→handle |
| M06 (v3 early) | wrong_tool | extra `social_search` | parallel hint quá rộng | v3: drop-Twitter → chỉ lookup |

## B3. Team eval cases

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01 | timeline vs search | `timeline(karpathy)` | PASS |
| G02 | news timeframe month | `lookup(AI,news,month)` | PASS |
| G03 | missing URL | `clarify(text)` | PASS |
| G04 | send boundary | `clarify(yes_no)` | PASS |
| G05 | out of scope recipe | `no_tool` | PASS |
| G06 | multi → fetch URL | `fetch(anthropic news)` | PASS |
| G07 | multi correct limit | `timeline(sama,2)` | PASS |
| G08 | multi fill then timeline | `timeline(elonmusk,4)` | PASS |
| G09 | multi cancel → meta | `no_tool` | PASS |
| G10 | drop Twitter → web only | `lookup(robotics,news,day)` | PASS |

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Research news | v3 | `lookup(query=AI, topic=news, timeframe=day)` | `transcripts/v3_openrouter_01095_PHANTRONGTIEN_live_research.transcript.json` | answered |
| Missing handle → fill | v3 | t1 `clarify(text)`; t2 `timeline(sama,limit=5)` | `..._live_clarify.transcript.json` | waiting → answered |
| Send boundary | v3 | `clarify(yes_no)` | `..._live_boundary.transcript.json` | waiting_for_user |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới `rank` | `tools/rank/`; smoke: local overlap rank | ranking items không cần API | Chỉ dùng khi user muốn rank; tránh extra call trên base eval |
| Optional built-in | `send` dry-run / confirm path | boundary needs_confirmation | Giữ Telegram creds unset trong `run_eval` |
| Bonus: tool mới thứ 4+ | — | chưa claim | — |

UI: `app.py` (Streamlit) reuse `run_model_tool_loop` — core deliverable, không tính bonus.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`? Clarify/confirm/OOS + map famous names + latest-turn switch.
- Which fixes belonged in `tools.yaml`? When-to-use/when-not, arg conventions (`topic`, `timeframe`, `search_type`), send confirmation boundary text.
- Which failure needed manual review instead of automatic grading? Tool execution errors trong `tool_results` (routing PASS ≠ fetch/search always healthy).
- What would you improve next? Thêm eval case cho `rank`; deploy tunnel URL bền hơn; giảm optional tools trong declaration nếu không demo.
