// fig_structure.asy — Cross-section view (구조도)
// Pure 2D: no import three, ASCII labels only

size(12cm, 0);
defaultpen(linewidth(0.7pt));

pen solid  = black + linewidth(0.9pt);
pen hidden = black + linewidth(0.45pt) + linetype("4 3");
pen thin   = black + linewidth(0.35pt);
pen center_pen = black + linewidth(0.4pt) + linetype("8 3 2 3");
pen hatch  = gray(0.55) + linewidth(0.4pt);

real BASE_R=20, BASE_H=8;
real FEED_R=2,  FEED_H=5;
real MID_R=6,   MID_T=1.5, MID_H=40;
real TOP_R=4,   TOP_H=20;

real zFeed = BASE_H;
real zMid  = BASE_H + FEED_H;
real zTop  = zMid + MID_H;
real zEnd  = zTop + TOP_H;

// ── Center line ─────────────────────────────────────
draw((0,-5)--(0,zEnd+8), center_pen);

// ── (1) Base plate ───────────────────────────────────
fill((-BASE_R,0)--(BASE_R,0)--(BASE_R,BASE_H)--(-BASE_R,BASE_H)--cycle, white);
draw((-BASE_R,0)--(BASE_R,0), solid);
draw((-BASE_R,0)--(-BASE_R,BASE_H), solid);
draw((BASE_R,0)--(BASE_R,BASE_H), solid);
draw((-BASE_R,BASE_H)--(-MID_R,BASE_H), solid);
draw((MID_R,BASE_H)--(BASE_R,BASE_H), solid);
// cross-hatch fill
for(real y=1.5; y<BASE_H; y+=2.5)
    draw((-BASE_R,y)--(BASE_R,y), hatch);

// ── (2) Feed pin ─────────────────────────────────────
fill((-FEED_R,zFeed)--(FEED_R,zFeed)
    --(FEED_R,zFeed+FEED_H)--(-FEED_R,zFeed+FEED_H)--cycle, white);
draw((-FEED_R,zFeed)--(-FEED_R,zFeed+FEED_H), solid);
draw((FEED_R,zFeed)--(FEED_R,zFeed+FEED_H), solid);
draw((-FEED_R,zFeed+FEED_H)--(FEED_R,zFeed+FEED_H), solid);

// ── (3) Sleeve (hollow tube) ─────────────────────────
// Outer walls
draw((-MID_R,zMid)--(-MID_R,zMid+MID_H), solid);
draw((MID_R,zMid)--(MID_R,zMid+MID_H), solid);
draw((-MID_R,zMid)--(MID_R,zMid), solid);          // bottom face
draw((-MID_R,zMid+MID_H)--(MID_R,zMid+MID_H), solid); // top face
// Inner walls (hidden)
draw((-MID_R+MID_T,zMid)--(-MID_R+MID_T,zMid+MID_H), hidden);
draw((MID_R-MID_T,zMid)--(MID_R-MID_T,zMid+MID_H), hidden);
// Section hatch on wall thickness
for(real y=zMid+2; y<zMid+MID_H-1; y+=3) {
    draw((-MID_R,y)--(-MID_R+MID_T,y), hatch);
    draw((MID_R-MID_T,y)--(MID_R,y), hatch);
}

// ── (4) Radiating element (cone) ─────────────────────
draw((-TOP_R,zTop)--(0,zTop+TOP_H), solid);
draw((TOP_R,zTop)--(0,zTop+TOP_H), solid);
draw((-TOP_R,zTop)--(TOP_R,zTop), solid);

// ── Dimension lines ───────────────────────────────────
real lx = BASE_R+5;

// (1) Base plate height
draw((BASE_R+1,0)--(lx+10,0), thin);
draw((BASE_R+1,BASE_H)--(lx+10,BASE_H), thin);
draw((lx+8,0)--(lx+8,BASE_H), thin, Arrows(3));
label("(1)", (lx+14, BASE_H/2), fontsize(8pt));

// (2) Feed pin
draw((FEED_R+1,zFeed)--(lx,zFeed), thin);
draw((FEED_R+1,zFeed+FEED_H)--(lx,zFeed+FEED_H), thin);
draw((lx-2,zFeed)--(lx-2,zFeed+FEED_H), thin, Arrows(3));
label("(2)", (lx+4, zFeed+FEED_H/2), fontsize(8pt));

// (3) Sleeve
draw((MID_R+1,zMid)--(lx,zMid), thin);
draw((MID_R+1,zMid+MID_H)--(lx,zMid+MID_H), thin);
draw((lx-2,zMid)--(lx-2,zMid+MID_H), thin, Arrows(3));
label("(3)", (lx+4, zMid+MID_H/2), fontsize(8pt));

// (4) Cone
draw((TOP_R+1,zTop)--(lx,zTop), thin);
draw((1,zTop+TOP_H)--(lx,zTop+TOP_H), thin);
draw((lx-2,zTop)--(lx-2,zTop+TOP_H), thin, Arrows(3));
label("(4)", (lx+4, zTop+TOP_H/2), fontsize(8pt));

// ── Labels ────────────────────────────────────────────
label("\textbf{Fig. 1 -- Structural Cross-Section}", (0,-9), fontsize(9pt));
label("(1) Base  (2) Feed Pin  (3) Sleeve  (4) Radiating Element",
      (0,-14), fontsize(7pt));
