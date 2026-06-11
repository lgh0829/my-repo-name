// fig_assembly.asy — Half-section assembly view (결합도)
// Left: internal cross-section  |  Right: external oblique silhouette

size(13cm, 0);
defaultpen(linewidth(0.7pt));

pen solid  = black + linewidth(0.9pt);
pen hidden = black + linewidth(0.4pt) + linetype("4 3");
pen thin   = black + linewidth(0.35pt);
pen center_pen = black + linewidth(0.4pt) + linetype("8 3 2 3");
pen hatch  = gray(0.5) + linewidth(0.4pt);

real BASE_R=20, BASE_H=8;
real FEED_R=2,  FEED_H=5;
real MID_R=6,   MID_T=1.5, MID_H=40;
real TOP_R=4,   TOP_H=20;
real zFeed=BASE_H, zMid=BASE_H+FEED_H, zTop=zMid+MID_H, zEnd=zTop+TOP_H;

// ═══════════════════════════════════════════════════
// LEFT HALF: Internal cross-section (x ≤ 0)
// ═══════════════════════════════════════════════════

// (1) Base plate — left half cross-section
fill((-BASE_R,0)--(0,0)--(0,BASE_H)--(-BASE_R,BASE_H)--cycle, white);
draw((-BASE_R,0)--(0,0), solid);
draw((-BASE_R,0)--(-BASE_R,BASE_H), solid);
draw((-BASE_R,BASE_H)--(-MID_R,BASE_H), solid);
for(real y=1.5; y<BASE_H; y+=2.5)
    draw((-BASE_R,y)--(0,y), hatch);

// (2) Feed pin — left half
fill((-FEED_R,zFeed)--(0,zFeed)--(0,zFeed+FEED_H)--(-FEED_R,zFeed+FEED_H)--cycle, white);
draw((-FEED_R,zFeed)--(-FEED_R,zFeed+FEED_H), solid);
draw((-FEED_R,zFeed+FEED_H)--(0,zFeed+FEED_H), solid);

// (3) Sleeve — left outer wall
draw((-MID_R,zMid)--(-MID_R,zMid+MID_H), solid);
draw((-MID_R,zMid)--(0,zMid), solid);
draw((-MID_R,zMid+MID_H)--(0,zMid+MID_H), solid);
// Left inner wall
draw((-MID_R+MID_T,zMid)--(-MID_R+MID_T,zMid+MID_H), hidden);
// Section hatch on left wall
for(real y=zMid+2; y<zMid+MID_H-1; y+=3)
    draw((-MID_R,y)--(-MID_R+MID_T,y), hatch);

// (4) Cone — left
fill((-TOP_R,zTop)--(0,zTop)--(0,zEnd)--cycle, white);
draw((-TOP_R,zTop)--(0,zEnd), solid);
draw((-TOP_R,zTop)--(0,zTop), solid);

// ═══════════════════════════════════════════════════
// RIGHT HALF: External oblique silhouette (x ≥ 0)
// ═══════════════════════════════════════════════════
real ew, eh;

// (1) Base plate — right outer silhouette
ew=BASE_R; eh=BASE_R*0.3;
draw((0,0)--(BASE_R,0), solid);
draw((BASE_R,0)--(BASE_R,BASE_H), solid);
draw((BASE_R,BASE_H)--(MID_R,BASE_H), solid);
// Top ellipse arc (right side, front half)
draw(shift(0,BASE_H)*xscale(ew)*yscale(eh)*arc((0,0),1,-90,0), solid);

// (3) Sleeve — right outer silhouette
ew=MID_R; eh=MID_R*0.35;
draw((MID_R,zMid)--(MID_R,zMid+MID_H), solid);
// Top ellipse of sleeve (right front quarter)
draw(shift(0,zMid+MID_H)*xscale(ew)*yscale(eh)*arc((0,0),1,-90,0), solid);
// Bottom ellipse right front quarter
draw(shift(0,zMid)*xscale(ew)*yscale(eh)*arc((0,0),1,-90,0), solid);

// (4) Cone — right silhouette
draw((0,zEnd)--(TOP_R,zTop), solid);
draw((TOP_R,zTop)--(MID_R,zTop), solid);

// ═══════════════════════════════════════════════════
// CENTER LINE
// ═══════════════════════════════════════════════════
draw((0,-5)--(0,zEnd+8), center_pen);

// Cut plane indicator (zigzag at x=0)
real zz=zEnd/2;
draw((-3,zz-3)--(0,zz)--(3,zz-3), thin+linewidth(0.5pt));

// ═══════════════════════════════════════════════════
// LEADER LINES & LABELS
// ═══════════════════════════════════════════════════
real lx = BASE_R+10;
void leader(real x1, real y1, string txt) {
    draw((x1,y1)--(lx-1,y1), thin, Arrow(3));
    label(txt, (lx+2, y1), E, fontsize(8pt));
}
leader(BASE_R,  BASE_H/2,         "(1) Base plate");
leader(FEED_R,  zFeed+FEED_H/2,   "(2) Feed pin");
leader(MID_R,   zMid+MID_H/2,     "(3) Sleeve");
leader(TOP_R*0.5, zTop+TOP_H*0.5, "(4) Element");

// ═══════════════════════════════════════════════════
// TITLE
// ═══════════════════════════════════════════════════
label("\textbf{Fig. 3 -- Half-Section Assembly}", (0,-9), fontsize(9pt));
label("Left: cross-section | Right: external view", (0,-14), fontsize(7pt));
