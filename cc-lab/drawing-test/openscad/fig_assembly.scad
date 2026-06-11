// 결합도 (Assembly View)
// 단면 컷(half-section)으로 내부 조립 상태를 동시에 보여준다

$fn = 64;

BASE_COLOR  = [0.85, 0.85, 0.85];
MID_COLOR   = [0.60, 0.80, 1.00];
TOP_COLOR   = [1.00, 0.75, 0.30];

BASE_R  = 20;  BASE_H  = 8;
MID_R   = 6;   MID_H   = 40;
TOP_R   = 4;   TOP_H   = 20;
FEED_R  = 2;   FEED_H  = 5;

TOTAL_H = BASE_H + FEED_H + MID_H + TOP_H + 2;
CUT_W   = 60;  // 단면 컷 절반 폭

// 전체 조립 모델 (절반 단면 컷 적용)
module full_assembly() {
    // 기저 플레이트
    color(BASE_COLOR)
        cylinder(r=BASE_R, h=BASE_H);

    // 피드 핀
    color([0.3, 0.3, 0.3])
        translate([0, 0, BASE_H])
            cylinder(r=FEED_R, h=FEED_H);

    // 중간 슬리브
    color(MID_COLOR)
        translate([0, 0, BASE_H + FEED_H])
            difference() {
                cylinder(r=MID_R,     h=MID_H);
                cylinder(r=MID_R-1.5, h=MID_H);
            }

    // 상단 방사 소자
    color(TOP_COLOR)
        translate([0, 0, BASE_H + FEED_H + MID_H])
            cylinder(r1=TOP_R, r2=TOP_R*0.4, h=TOP_H);
}

// 단면 컷: +Y 반쪽만 제거해 내부 단면 노출
difference() {
    full_assembly();
    // Y 양수 방향 절반 제거
    translate([-CUT_W/2, 0, -1])
        cube([CUT_W, CUT_W, TOTAL_H + 2]);
}

// 단면 윤곽선 강조 (얇은 회색 면)
color([0.5, 0.5, 0.5, 0.3])
    translate([-CUT_W/2, -0.3, -1])
        cube([CUT_W, 0.6, TOTAL_H + 2]);
