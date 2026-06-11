// 사시도 — 분리(Exploded) 뷰
// 각 부품을 Z축 방향으로 떼어내어 내부 구조가 보이도록 표현

$fn = 64;

BASE_COLOR  = [0.85, 0.85, 0.85];
MID_COLOR   = [0.60, 0.80, 1.00];
TOP_COLOR   = [1.00, 0.75, 0.30];

BASE_R  = 20;  BASE_H  = 8;
MID_R   = 6;   MID_H   = 40;
TOP_R   = 4;   TOP_H   = 20;
FEED_R  = 2;   FEED_H  = 5;

// 분리 간격
GAP = 18;

// ① 기저 플레이트 — 원래 위치
color(BASE_COLOR)
    cylinder(r=BASE_R, h=BASE_H);

// ② 동축 피드 핀 — GAP 만큼 위로 분리
color([0.3, 0.3, 0.3])
    translate([0, 0, BASE_H + GAP])
        cylinder(r=FEED_R, h=FEED_H);

// 연결 점선 표현 (얇은 실린더)
color([0.7, 0.7, 0.7])
    translate([0, 0, BASE_H])
        cylinder(r=0.4, h=GAP);

// ③ 중간 슬리브 — 2×GAP 만큼 위로 분리
color(MID_COLOR)
    translate([0, 0, BASE_H + FEED_H + 2*GAP])
        difference() {
            cylinder(r=MID_R,     h=MID_H);
            cylinder(r=MID_R-1.5, h=MID_H);
        }

color([0.7, 0.7, 0.7])
    translate([0, 0, BASE_H + FEED_H + GAP])
        cylinder(r=0.4, h=GAP);

// ④ 상단 방사 소자 — 3×GAP 만큼 위로 분리
color(TOP_COLOR)
    translate([0, 0, BASE_H + FEED_H + MID_H + 3*GAP])
        cylinder(r1=TOP_R, r2=TOP_R*0.4, h=TOP_H);

color([0.7, 0.7, 0.7])
    translate([0, 0, BASE_H + FEED_H + MID_H + 2*GAP])
        cylinder(r=0.4, h=GAP);
