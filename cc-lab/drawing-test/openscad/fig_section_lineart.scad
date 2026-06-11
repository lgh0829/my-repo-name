// 구조도 단면 선화 — projection(cut=true) 로 Y=0 단면을 2D 선화로 추출
// SVG 출력 시 흑백 벡터 라인만 생성됨

$fn = 64;

BASE_R  = 20;  BASE_H  = 8;
MID_R   = 6;   MID_H   = 40;
TOP_R   = 4;   TOP_H   = 20;
FEED_R  = 2;   FEED_H  = 5;

// projection(cut=true) : Z=0 평면으로 슬라이스한 단면 윤곽을 2D로 추출
// 전체 구조를 90도 눕혀서 측면 단면이 나오게 함
projection(cut=true)
rotate([90, 0, 0])          // X축으로 세워서 XZ 평면이 단면이 되게
translate([0, 0, 0]) {

    // 기저 플레이트
    cylinder(r=BASE_R, h=BASE_H);

    // 피드 핀
    translate([0, 0, BASE_H])
        cylinder(r=FEED_R, h=FEED_H);

    // 중간 슬리브 (속이 빈 튜브)
    translate([0, 0, BASE_H + FEED_H])
        difference() {
            cylinder(r=MID_R,     h=MID_H);
            cylinder(r=MID_R-1.5, h=MID_H);
        }

    // 상단 방사 소자
    translate([0, 0, BASE_H + FEED_H + MID_H])
        cylinder(r1=TOP_R, r2=TOP_R*0.4, h=TOP_H);
}
