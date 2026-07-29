# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 11:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team: G16 (E403)
- Members: 
  - Vũ Việt Anh (2A202601107)
  - Kiều Thế Hiệp (2A202601435)
  - Phó Viết Tiến Anh (2A202601341)
  - Trần Bảo Ninh (2A202601595)
  - Phan Trọng Tiến (2A202601095)
  - Nguyễn Văn Duy (2A202601749)
- Provider/model: OpenRouter (openai/gpt-4o-mini)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì.

Ví dụ: "Research Agent chuẩn Enterprise: Tìm kiếm tin tức tức thời trên Web và Twitter, tổng hợp thông tin, tóm tắt video Youtube, tra cứu giá Crypto/Thời tiết/Github trending, và trình bày bằng Markdown chuyên nghiệp."

**Link dùng thử (truy cập được trong showdown):**

> URL: **http://127.0.0.1:8000** (Sẽ cung cấp Cloudflare Tunnel URL khi bắt đầu Showdown)

## A2. Tool agent có

> Liệt kê các tool agent đang dùng. Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| timeline | lấy các bài đăng gần đây của một tài khoản Twitter | không |
| social_search | tìm bài đăng trên mạng xã hội theo từ khóa | không |
| lookup | tra cứu thông tin hoặc tin tức trên internet | không |
| fetch | đọc và lấy nội dung text từ một URL cụ thể | không |
| format | trình bày dữ liệu đã thu thập thành markdown report | không |
| send | gửi nội dung đến một hệ thống bên ngoài | không |
| youtube_summarizer | Tóm tắt nội dung video Youtube từ URL | **Có (Bonus)** |
| weather_forecast | Lấy thông tin thời tiết tại một địa điểm | **Có (Bonus)** |
| crypto_tracker | Tra cứu giá tiền điện tử (Bitcoin, ETH...) | **Có (Bonus)** |
| github_explorer | Lấy danh sách repository đang trending trên Github | **Có (Bonus)** |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. "Tìm tin tức mới nhất về OpenAI hôm nay." (Sử dụng `lookup` với topic news)
2. "Lấy 5 tweet gần nhất của Elon Musk." (Sử dụng `timeline`)
3. "Tóm tắt video Youtube này giúp tôi: [URL]" (Sử dụng `youtube_summarizer` - Tool mới)
4. "Giá Bitcoin hiện tại là bao nhiêu và thời tiết ở Tokyo đang như thế nào?" (Parallel tools: `crypto_tracker` + `weather_forecast`)

## A4. Kịch bản demo đã rehearse

> Chuẩn bị 3–5 scenario. Mỗi scenario cần cho thấy tool đã làm gì và một thay đổi cụ thể giữa các version.

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Mơ hồ / Thiếu thông tin | `clarify` | Ở `v0`, agent tự đoán mò tên (Sam Altman). Lên `v1`, agent biết dùng `clarify` để hỏi lại user. | `transcripts/scenario_missing_info.json` |
| Yêu cầu đa luồng (Parallel) | `lookup` + `timeline` đồng thời | Ở `v0`, agent chỉ gọi 1 tool rồi dừng. Lên `v1`, agent có thể gọi song song nhiều tools để lấy thông tin toàn diện. | `transcripts/scenario_parallel.json` |
| Sử dụng công cụ Bonus | `youtube_summarizer` | Giới thiệu năng lực mới (không có trong đề bài) do nhóm tự code thêm để lấy điểm tuyệt đối. | `transcripts/scenario_bonus.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn
- 5 multi-turn

This section is for the mandatory team-authored eval set. Optional built-ins do
not belong here.

File template để trống có chủ đích; nhóm phải tự thiết kế đủ 10 case.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/PDF nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên |  |  |  |
| Optional built-in |  |  |  |
| Bonus: tool mới thứ 4 trở đi |  |  |  |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
