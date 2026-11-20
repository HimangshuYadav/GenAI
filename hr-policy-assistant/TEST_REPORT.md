# HR Policy Assistant - Test & Verification Report

**Execution Date:** 2026-11-20 10:48:37
**Document Tested:** NovaPay Global HR Manual (50 Pages, 194 Chunks)
**Embedding Model:** `BAAI/bge-small-en-v1.5`
**Vector Store:** ChromaDB (Cosine Similarity + BM25 Reciprocal Rank Fusion)
**LLM Target:** Groq `llama-3.3-70b-versatile`

## Test Summary

- **Total Tests Executed:** 15
- **Passed:** 15 / 15
- **Failed:** 0

## Detailed Test Cases

### [COMP-1] Compensation

**Question:** What are the promotion cycles and annual performance calibration guidelines for employment grades?

**Expected In Scope:** `Yes`

**Generated Answer:**

> Based on the employee handbook, here is the official policy regarding compensation:
> 
> • AND PROMOTION CYCLES (CHAPTER 1 | MODULE 1.0: GLOBAL EMPLOYMENT GRADES, ANNUAL PERFORMANCE CALIBRATION,, p. 1)
> 
> ℹ️ *Note: This response is for informational purposes only. Human Resources is the final authority on policy interpretation.*

**Retrieved Sources:**
- `CHAPTER 1 | MODULE 1.0: GLOBAL EMPLOYMENT GRADES, ANNUAL PERFORMANCE CALIBRATION,` (Page 1, Similarity: 0.85)
- `CHAPTER 2 | MODULE 16.0: GLOBAL EMPLOYMENT GRADES, ANNUAL PERFORMANCE CALIBRATION,` (Page 16, Similarity: 0.85)

**Test Verdict:** `PASSED`

---

### [COMP-2] Compensation

**Question:** How are employment grades and baseline operational standards reviewed across operational cycles?

**Expected In Scope:** `Yes`

**Generated Answer:**

> Based on the employee handbook, here is the official policy regarding compensation:
> 
> • Promotion Cycles (Reference Clause 21.1) This section of ’NovaPay Global Human Resources, Compensation & Benefits Manual’ establishes the baseline operational procedures, governance standards, and quality (CHAPTER 3 | MODULE 21.0: GLOBAL EMPLOYMENT GRADES, ANNUAL PERFORMANCE CALIBRATION, - 1. Overview of Global Employment Grades, Annual Performance Calibration, and, p. 21)
> 
> ℹ️ *Note: This response is for informational purposes only. Human Resources is the final authority on policy interpretation.*

**Retrieved Sources:**
- `CHAPTER 3 | MODULE 21.0: GLOBAL EMPLOYMENT GRADES, ANNUAL PERFORMANCE CALIBRATION, - 1. Overview of Global Employment Grades, Annual Performance Calibration, and` (Page 21, Similarity: 0.83)
- `CHAPTER 1 | MODULE 1.0: GLOBAL EMPLOYMENT GRADES, ANNUAL PERFORMANCE CALIBRATION, - 1. Overview of Global Employment Grades, Annual Performance Calibration, and` (Page 1, Similarity: 0.83)

**Test Verdict:** `PASSED`

---

### [ESOP-1] ESOPs

**Question:** What is the vesting schedule and cliff for Band-3 engineers under the NovaPay 2026 ESOP Plan?

**Expected In Scope:** `Yes`

**Generated Answer:**

> Based on the employee handbook, here is the official policy regarding esops:
> 
> • Full-time Band-3 and above engineers receive equity grants under the NovaPay 2026 ESOP Plan. All Band-3 ESOP grants are governed by a mandatory 1-year (12-month) cliff period, at the completion of which 25% of the granted options vest. The (SECTION 3.1: EMPLOYEE STOCK OWNERSHIP PLAN (ESOP) VESTING SCHEDULE, p. 11)
> 
> ℹ️ *Note: This response is for informational purposes only. Human Resources is the final authority on policy interpretation.*

**Retrieved Sources:**
- `SECTION 3.1: EMPLOYEE STOCK OWNERSHIP PLAN (ESOP) VESTING SCHEDULE` (Page 11, Similarity: 0.86)
- `CHAPTER 3 | MODULE 25.0:  SABBATICAL ELIGIBILITY, NOTICE PERIOD BUYOUTS, AND EXIT` (Page 25, Similarity: 0.60)

**Test Verdict:** `PASSED`

---

### [ESOP-2] ESOPs

**Question:** What percentage of options vest after the 12-month cliff and how does the remaining 75% vest?

**Expected In Scope:** `Yes`

**Generated Answer:**

> Based on the employee handbook, here is the official policy regarding esops:
> 
> • Full-time Band-3 and above engineers receive equity grants under the NovaPay 2026 ESOP Plan. All Band-3 ESOP grants are governed by a mandatory 1-year (12-month) cliff period, at the completion of which 25% of the granted options vest. The (SECTION 3.1: EMPLOYEE STOCK OWNERSHIP PLAN (ESOP) VESTING SCHEDULE, p. 11)
> 
> ℹ️ *Note: This response is for informational purposes only. Human Resources is the final authority on policy interpretation.*

**Retrieved Sources:**
- `SECTION 3.1: EMPLOYEE STOCK OWNERSHIP PLAN (ESOP) VESTING SCHEDULE` (Page 11, Similarity: 0.74)
- `CHAPTER 2 | MODULE 12.0: INFORMATION SECURITY, CLEAN DESK POLICY, AND INSIDER` (Page 12, Similarity: 0.61)

**Test Verdict:** `PASSED`

---

### [CAFE-1] Cafeteria

**Question:** What are the cafeteria operating hours and meal subsidy policies for employees?

**Expected In Scope:** `No (Must trigger not found)`

**Generated Answer:**

> I couldn't find this in the employee handbook. Please contact HR at hr@company.com.

**Retrieved Sources:** None (Correctly filtered as out-of-scope/unmatched)

**Test Verdict:** `PASSED`

---

### [CAFE-2] Cafeteria

**Question:** Is there a free barista coffee service or meal voucher provided in the cafeteria?

**Expected In Scope:** `No (Must trigger not found)`

**Generated Answer:**

> I couldn't find this in the employee handbook. Please contact HR at hr@company.com.

**Retrieved Sources:** None (Correctly filtered as out-of-scope/unmatched)

**Test Verdict:** `PASSED`

---

### [TRAV-1] Travel Reimbursement

**Question:** What is the maximum daily hotel lodging reimbursement cap for international travel in Tier-1 cities?

**Expected In Scope:** `Yes`

**Generated Answer:**

> Based on the employee handbook, here is the official policy regarding travel reimbursement:
> 
> • Employees traveling internationally on approved company business must book accommodations through the corporate travel portal. For Tier-1 international cities (specifically London, New York, Tokyo, Zurich, and Singapore), the maximum (SECTION 6.2: INTERNATIONAL BUSINESS TRAVEL & HOTEL LODGING CAPS, p. 27)
> 
> ℹ️ *Note: This response is for informational purposes only. Human Resources is the final authority on policy interpretation.*

**Retrieved Sources:**
- `SECTION 6.2: INTERNATIONAL BUSINESS TRAVEL & HOTEL LODGING CAPS` (Page 27, Similarity: 0.90)
- `CHAPTER 5 | MODULE 45.0:  SABBATICAL ELIGIBILITY, NOTICE PERIOD BUYOUTS, AND EXIT` (Page 45, Similarity: 0.62)

**Test Verdict:** `PASSED`

---

### [TRAV-2] Travel Reimbursement

**Question:** Which international cities are classified as Tier-1 and who must approve hotel receipts exceeding $350 USD per night?

**Expected In Scope:** `Yes`

**Generated Answer:**

> Based on the employee handbook, here is the official policy regarding travel reimbursement:
> 
> • Employees traveling internationally on approved company business must book accommodations through the corporate travel portal. For Tier-1 international cities (specifically London, New York, Tokyo, Zurich, and Singapore), the maximum (SECTION 6.2: INTERNATIONAL BUSINESS TRAVEL & HOTEL LODGING CAPS, p. 27)
> 
> ℹ️ *Note: This response is for informational purposes only. Human Resources is the final authority on policy interpretation.*

**Retrieved Sources:**
- `SECTION 6.2: INTERNATIONAL BUSINESS TRAVEL & HOTEL LODGING CAPS` (Page 27, Similarity: 0.73)
- `CHAPTER 4 | MODULE 35.0:  SABBATICAL ELIGIBILITY, NOTICE PERIOD BUYOUTS, AND EXIT` (Page 35, Similarity: 0.56)

**Test Verdict:** `PASSED`

---

### [LEAV-1] Leave Policies

**Question:** What are the parental and paternity leave entitlements for full-time employees?

**Expected In Scope:** `Yes`

**Generated Answer:**

> Based on the employee handbook, here is the official policy regarding leave policies:
> 
> • All full-time NovaPay employees globally are entitled to 6 weeks (30 working days) of 100% paid paternity leave following the birth or legal adoption of a child. This 6-week paid paternity leave must be taken within 6 months (26 weeks) of the (SECTION 8.4: PARENTAL & PATERNITY LEAVE ENTITLEMENTS, p. 39)
> 
> ℹ️ *Note: This response is for informational purposes only. Human Resources is the final authority on policy interpretation.*

**Retrieved Sources:**
- `SECTION 8.4: PARENTAL & PATERNITY LEAVE ENTITLEMENTS` (Page 39, Similarity: 0.77)
- `CHAPTER 5 | MODULE 44.0: HYBRID WORK ATTENDANCE EXPECTATIONS AND HOME-OFFICE` (Page 44, Similarity: 0.64)

**Test Verdict:** `PASSED`

---

### [LEAV-2] Leave Policies

**Question:** Within what timeframe must the 6-week paid paternity leave be utilized following childbirth or adoption?

**Expected In Scope:** `Yes`

**Generated Answer:**

> Based on the employee handbook, here is the official policy regarding leave policies:
> 
> • All full-time NovaPay employees globally are entitled to 6 weeks (30 working days) of 100% paid paternity leave following the birth or legal adoption of a child. This 6-week paid paternity leave must be taken within 6 months (26 weeks) of the (SECTION 8.4: PARENTAL & PATERNITY LEAVE ENTITLEMENTS, p. 39)
> 
> ℹ️ *Note: This response is for informational purposes only. Human Resources is the final authority on policy interpretation.*

**Retrieved Sources:**
- `SECTION 8.4: PARENTAL & PATERNITY LEAVE ENTITLEMENTS` (Page 39, Similarity: 0.83)
- `CHAPTER 5 | MODULE 50.0:  SABBATICAL ELIGIBILITY, NOTICE PERIOD BUYOUTS, AND EXIT - 1. Overview of  Sabbatical Eligibility, Notice Period Buyouts, and Exit Clearance` (Page 50, Similarity: 0.63)

**Test Verdict:** `PASSED`

---

### [BENF-1] Employee Benefits

**Question:** What are the attendance expectations for hybrid work and home-office ergonomic stipends?

**Expected In Scope:** `Yes`

**Generated Answer:**

> Based on the employee handbook, here is the official policy regarding employee benefits:
> 
> • ERGONOMIC STIPENDS (CHAPTER 1 | MODULE 4.0: HYBRID WORK ATTENDANCE EXPECTATIONS AND HOME-OFFICE, p. 4)
> 
> ℹ️ *Note: This response is for informational purposes only. Human Resources is the final authority on policy interpretation.*

**Retrieved Sources:**
- `CHAPTER 1 | MODULE 4.0: HYBRID WORK ATTENDANCE EXPECTATIONS AND HOME-OFFICE` (Page 4, Similarity: 0.91)
- `CHAPTER 2 | MODULE 19.0: HYBRID WORK ATTENDANCE EXPECTATIONS AND HOME-OFFICE` (Page 19, Similarity: 0.92)

**Test Verdict:** `PASSED`

---

### [BENF-2] Employee Benefits

**Question:** What are the policies regarding sabbatical eligibility, notice period buyouts, and exit clearance?

**Expected In Scope:** `Yes`

**Generated Answer:**

> Based on the employee handbook, here is the official policy regarding employee benefits:
> 
> • CLEARANCE WORKFLOWS (CHAPTER 2 | MODULE 15.0:  SABBATICAL ELIGIBILITY, NOTICE PERIOD BUYOUTS, AND EXIT, p. 15)
> 
> ℹ️ *Note: This response is for informational purposes only. Human Resources is the final authority on policy interpretation.*

**Retrieved Sources:**
- `CHAPTER 2 | MODULE 15.0:  SABBATICAL ELIGIBILITY, NOTICE PERIOD BUYOUTS, AND EXIT` (Page 15, Similarity: 0.86)
- `CHAPTER 4 | MODULE 35.0:  SABBATICAL ELIGIBILITY, NOTICE PERIOD BUYOUTS, AND EXIT` (Page 35, Similarity: 0.87)

**Test Verdict:** `PASSED`

---

### [OOS-1] Out of Scope

**Question:** Who won the cricket world cup?

**Expected In Scope:** `No (Must trigger not found)`

**Generated Answer:**

> I couldn't find this in the employee handbook. Please contact HR at hr@company.com.

**Retrieved Sources:** None (Correctly filtered as out-of-scope/unmatched)

**Test Verdict:** `PASSED`

---

### [OOS-2] Out of Scope

**Question:** What is the capital of France and what are the best tourist attractions in Paris?

**Expected In Scope:** `No (Must trigger not found)`

**Generated Answer:**

> I couldn't find this in the employee handbook. Please contact HR at hr@company.com.

**Retrieved Sources:** None (Correctly filtered as out-of-scope/unmatched)

**Test Verdict:** `PASSED`

---

### [OOS-3] Out of Scope

**Question:** Can you write Python code to sort a list of numbers?

**Expected In Scope:** `No (Must trigger not found)`

**Generated Answer:**

> I couldn't find this in the employee handbook. Please contact HR at hr@company.com.

**Retrieved Sources:** None (Correctly filtered as out-of-scope/unmatched)

**Test Verdict:** `PASSED`

---

