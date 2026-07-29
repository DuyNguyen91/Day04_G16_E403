# Day 04 Lab v2 Report — G16 Research Agent

## Team

- Team: G16
- Members: chưa được cung cấp trong workspace
- Provider/model: Groq / `qwen/qwen3.6-27b`
- Local UI: `http://localhost:8501` via `streamlit run app.py`

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent tìm tin web, bài đăng theo tài khoản/chủ đề, đọc URL, định dạng
digest, kiểm tra chất lượng nguồn và giữ confirmation boundary trước khi gửi.
UI hiển thị request/response, artifact version, từng tool call + args + result/error,
và lưu transcript JSON.

Chưa tạo public tunnel; URL local dùng được trên máy demo. Không đưa `.env` hoặc
secret lên UI/public tunnel.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | hỏi thiếu account/URL hoặc xác nhận side effect | không |
| `timeline` | lấy post mới của một account | không |
| `social_search` | tìm post về một chủ đề | không |
| `lookup` | tìm web/news theo timeframe | không |
| `fetch` | đọc URL cụ thể | không |
| `format` | định dạng items có sẵn | không |
| `source_audit` | kiểm tra URL, metadata và độ đa dạng domain | **có** |
| `send` | gửi Telegram sau xác nhận | optional built-in |
| `policy`, `papers`, `paper_text` | policy/arXiv/PDF | optional built-in |

## A3. Câu hỏi mẫu để thử

1. `Tin AI hôm nay có gì nổi bật?`
2. `Lấy 7 tweet mới nhất của Andrej Karpathy.`
3. `Mọi người đang bàn gì về AI agents trên Twitter?`
4. `Tóm tắt bài này: https://example.com`
5. `Đăng bản tin này lên Telegram giúp mình.` (phải hỏi xác nhận)

## A4. Kịch bản demo đã chuẩn bị

| Scenario | Tool trace cần thấy | Câu chuyện version | Fallback evidence |
|---|---|---|---|
| Thiếu account | `clarify(text)` | v0 đoán; v1 cấm đoán | v1 base run |
| Tin web + social | `lookup` + `social_search` | Groq v3 còn thiếu call thứ hai ở R13 | v3 base Groq |
| Publish | `clarify(yes_no)` | v1/v2 làm rõ boundary; Groq v3 PASS | transcript Groq |
| Kiểm tra sources | `source_audit` | tool mới deterministic | direct quick-test |

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version evidence

Các run v0–v2 dùng OpenRouter free là evidence quá trình nhưng không đạt provider
gate. Run Groq v3/v4 đo đủ 20/20 case với `provider_error_cases=0`; metric v3 là
evidence chính của artifact cuối.

| Version | Thay đổi / hypothesis | Measured / total | Provider errors | Measured case accuracy | Run |
|---|---|---:|---:|---:|---|
| v0 | starter baseline cố ý mơ hồ | 3/20 | 17 | 0.6667 | `runs/v0_B_base_openrouter_20260729T102921523130.json` |
| v1 | prompt: scope, clarification, confirmation, carry-over | 15/20 | 5 | 0.8000 | `runs/v1_B_base_openrouter_20260729T103344747315.json` |
| v2 | tool descriptions: canonical query + boundary | 12/20 | 8 | 1.0000 | `runs/v2_B_base_openrouter_20260729T103847643624.json` |
| v3 | artifact cuối + Groq/Qwen | 20/20 | 0 | **0.9500** | `runs/v3_B_base_groq_20260729T111953747475.json` |
| v4 | thử ép parallel calls; regression, đã rollback | 20/20 | 0 | 0.9000 | `runs/v4_B_base_groq_20260729T112710259311.json` |

Artifact được chọn là `v3+pe2d16ad844e4+t10d635a6e009`. Base và group Groq
dùng cùng hash. v4 bị bác bỏ vì giảm case accuracy từ 0.95 xuống 0.90 và đã rollback.

## B2. Failure analysis

| Case | Failure | Actual | Fix / conclusion |
|---|---|---|---|
| v1 R03 | query quá dài | `lookup(query="tin tức AI nổi bật hôm nay")` | v2 declaration yêu cầu concise subject |
| v1 M02 | query quá dài | `lookup(query="robotics news")` | v2 declaration không thêm `news` |
| v1 R12 | wrong boundary | `clarify(response_type="text")` | v2 declaration + v3 priority rule |
| Groq v3 R13 | missing tool | chỉ `lookup`, thiếu `social_search` | v4 thử wording mạnh hơn nhưng không sửa được và gây regression; rollback |
| Groq v4 M05 | wrong limit | regression sau prompt change | bác bỏ v4 |
| OpenRouter runs | provider errors | response rỗng/429 | thay bằng Groq cho final evidence |

## B3. Team eval cases

`data/eval_group.json` có đúng 10 case: 5 `query`, 5 `turns`.

| Case | Mục tiêu | Expected |
|---|---|---|
| G16_S01 | topic vs account | `social_search` |
| G16_S02 | month + limit | `lookup` |
| G16_S03 | missing URL | `clarify(text)` |
| G16_S04 | publish boundary | `clarify(yes_no)` |
| G16_S05 | out of scope | no tool |
| G16_M01 | corrected subject | `lookup` |
| G16_M02 | corrected URL | `fetch` |
| G16_M03 | cancel prior intent | no tool |
| G16_M04 | corrected account + limit | `timeline` |
| G16_M05 | switch web → social | `social_search` |

Group run `runs/v3_B_group_groq_20260729T113057924759.json`: **10/10 PASS**,
`provider_error_cases=0`, routing/argument/multi-turn accuracy đều **1.0**.

## B4. Live chat evidence

- `transcripts/v3_groq_20260729T113332478611.transcript.json`: `timeline` PASS,
  missing URL → `clarify(text)` PASS, bổ sung URL → `fetch` PASS.
- `transcripts/v3_groq_20260729T113620996870.transcript.json`: publish request →
  `clarify(response_type="yes_no")` PASS.
- Một news-digest attempt vượt Groq TPM 8k do tool result lớn; đây là giới hạn cần
  giảm bằng cách truncate tool-result payload trong cải tiến sau.

## B5. Tool capability evidence

| Category | Evidence | What worked | Guardrail |
|---|---|---|---|
| Must-have new tool | `tools/source_audit/` | registry + YAML + direct test: 2 valid items, 2 domains, `ready=true` | read-only, no network |
| Core APIs | terminal smoke tests | Tavily, Firecrawl, timeline, social search đều `error=None` | chỉ summary, không log key |
| UI | `app.py` | compile PASS, server 8501, health `ok` | không render `.env`; errors captured |

## B6. Reflection

- Scope, confirmation priority và multi-turn precedence thuộc system prompt.
- Intent boundaries và argument conventions thuộc tool descriptions/schema.
- Provider errors và tool execution errors cần review thủ công; routing PASS không
  chứng minh API result đúng.
- v3 base đạt 19/20; lỗi còn lại là parallel routing R13.
- Cải tiến tiếp theo nên thay đổi orchestration hoặc chọn model parallel-call tốt
  hơn, đồng thời truncate tool-result payload để tránh Groq TPM 8k.
