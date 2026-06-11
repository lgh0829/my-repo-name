// 구조도 (Structural Diagram)
// 3단 원통 안테나 구조 — 각 부품의 위치·크기 관계를 보여준다

$fn = 64;

// ── 색상 팔레트 ──────────────────────────────
BASE_COLOR  = [0.85, 0.85, 0.85];   // 연회색  — 기저부
MID_COLOR   = [0.60, 0.80, 1.00];   // 하늘색  — 중간 도체
TOP_COLOR   = [1.00, 0.75, 0.30];   // 황금색  — 상단 방사체

// ── 치수 ─────────────────────────────────────
BASE_R  = 20;  BASE_H  = 8;
MID_R   = 6;   MID_H   = 40;
TOP_R   = 4;   TOP_H   = 20;
FEED_R  = 2;   FEED_H  = 5;

// ── 부품 정의 ─────────────────────────────────

// (1) 기저 플레이트
module base_plate() {
    color(BASE_COLOR)
    cylinder(r=BASE_R, h=BASE_H, center=false);
}

// (2) 동축 피드 핀
module feed_pin() {
    color([0.3, 0.3, 0.3])
    translate([0, 0, BASE_H])
        cylinder(r=FEED_R, h=FEED_H, center=false);
}

// (3) 중간 도체 슬리브
module mid_sleeve() {
    color(MID_COLOR)
    translate([0, 0, BASE_H + FEED_H])
        difference() {
            cylinder(r=MID_R,     h=MID_H, center=false);
            cylinder(r=MID_R-1.5, h=MID_H, center=false);
        }
}

// (4) 상단 방사 소자
module top_element() {
    color(TOP_COLOR)
    translate([0, 0, BASE_H + FEED_H + MID_H])
        cylinder(r1=TOP_R, r2=TOP_R*0.4, h=TOP_H, center=false);
}

// ── 조립 ─────────────────────────────────────
base_plate();
feed_pin();
mid_sleeve();
top_element();
