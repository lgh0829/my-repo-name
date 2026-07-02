---
aliases: 기존 고객 이메일 뉴스레터 템플릿 안내
작성일: 2026-07-02
수정일: 2026-07-02
상태: 초안
tags: newsletter, template, patsol
관련문서:
  - "[[PS-1122]]"
  - "[[content-classification-existing-customer-email]]"
  - "[[design-newsletter-email-system]]"
상위문서: "[[content-classification-existing-customer-email]]"
---

# 기존 고객 이메일 뉴스레터 템플릿

디자인 규격은 `design-newsletter-email-system.md`, 월간 카드형 시안은 `prototype-newsletter-monthly-existing-customer.html`을 기준으로 한다.

## 템플릿 목록

| 파일 | 용도 | 시스템 템플릿 |
|---|---|---|
| `newsletter-monthly-existing-customer.md` | 월간 주요 소식 3~5개 | 기본(1) |
| `newsletter-feature-existing-customer.md` | 주요 기능 추가 | 매거진(2) |
| `newsletter-improvement-existing-customer.md` | 기존 기능 개선 | 기본(1) |
| `newsletter-hotfix-existing-customer.md` | 고객 영향이 있는 긴급 수정 | 심플(4) |
| `newsletter-pilot-existing-customer.md` | 파일럿 참여 및 의견 수집 | 카드형(3) |

## 사용 방법

1. 목적에 맞는 템플릿 파일을 복사한다.
2. `{{...}}` 자리표시자를 실제 내용으로 교체한다.
3. 변리사와 기업 IP 담당자의 이용 가능 기능을 확인한다.
4. 캠페인 ID를 `YYYY-MM-{role}-{type}` 형식으로 변경한다.
5. 필요하면 공개 이미지 URL을 섹션에 `![](https://...)` 형식으로 추가한다.
6. 관리자 화면에서 `.md` 파일을 불러오고 미리보기와 버튼 링크를 확인한다.

## 제품 화면 캡처 사용

- 각 템플릿의 `![]({{...}})` 줄은 선택형 캡처 영역이다.
- 캡처를 사용하지 않으면 해당 줄 전체를 삭제한다.
- 이미지는 로그인 없이 외부에서 접근 가능한 URL이어야 한다.
- 전체 화면보다 고객이 확인해야 할 기능 영역을 중심으로 잘라낸다.
- 권장 비율은 16:10, 권장 원본 크기는 1200×750px이다.
- 개인정보, 고객명, 출원번호, 공개 전 데이터가 보이지 않는지 확인한다.
- 캡처 안의 작은 글자에 설명을 맡기지 않고, 핵심 내용은 본문에도 작성한다.

## 역할 코드

- 변리사: `attorney`
- 기업 IP 담당자: `corporate-ip`
- 두 역할 공통: `all-customer`

청구항 설계와 명세서 작성 지원 콘텐츠에는 `corporate-ip` 또는 `all-customer`를 사용하지 않는다.
