// fig_exploded.asy — Exploded oblique view (사시도)
// Cylinders drawn as oblique projections in pure 2D

size(11cm, 0);
defaultpen(linewidth(0.7pt));

pen solid  = black + linewidth(0.9pt);
pen hidden = black + linewidth(0.4pt) + linetype("4 3");
pen dash   = black + linewidth(0.5pt) + linetype("5 4");
pen thin   = black + linewidth(0.35pt);

// ── Oblique cylinder primitive ────────────────────────
// Draws a vertical cylinder in front-oblique view
// bottom center (cx,cy), radius r, height h
// ew = ellipse half-width, eh = foreshortened half-height
void cyl(real cx, real cy, real r, real h) {
    real ew = r, eh = r*0.38;

    // Bottom ellipse: front half solid, back half hidden
    path bot_front = shift(cx,cy)*xscale(ew)*yscale(eh)*arc((0,0),1,180,360);
    path bot_back  = shift(cx,cy)*xscale(ew)*yscale(eh)*arc((0,0),1,0,180);
    draw(bot_front, solid);
    draw(bot_back,  hidden);

    // Fill body white (to hide what's behind)
    fill((-ew+cx,cy)--(ew+cx,cy)--(ew+cx,cy+h)--(-ew+cx,cy+h)--cycle, white);

    // Side lines
    draw((cx-ew,cy)--(cx-ew,cy+h), solid);
    draw((cx+ew,cy)--(cx+ew,cy+h), solid);

    // Top ellipse (fully visible)
    fill(shift(cx,cy+h)*xscale(ew)*yscale(eh)*unitcircle, white);
    draw(shift(cx,cy+h)*xscale(ew)*yscale(eh)*unitcircle, solid);
}

// ── Oblique hollow cylinder (sleeve) ─────────────────
void hollow_cyl(real cx, real cy, real r, real t, real h) {
    real ew = r, eh = r*0.38;
    real iw = r-t, ih = (r-t)*0.38;

    // Bottom outer ellipse
    draw(shift(cx,cy)*xscale(ew)*yscale(eh)*arc((0,0),1,180,360), solid);
    draw(shift(cx,cy)*xscale(ew)*yscale(eh)*arc((0,0),1,0,180), hidden);
    // Bottom inner ellipse
    draw(shift(cx,cy)*xscale(iw)*yscale(ih)*arc((0,0),1,180,360), solid);
    draw(shift(cx,cy)*xscale(iw)*yscale(ih)*arc((0,0),1,0,180), hidden);

    fill((-ew+cx,cy)--(ew+cx,cy)--(ew+cx,cy+h)--(-ew+cx,cy+h)--cycle, white);

    // Outer side lines
    draw((cx-ew,cy)--(cx-ew,cy+h), solid);
    draw((cx+ew,cy)--(cx+ew,cy+h), solid);
    // Inner side lines (hidden)
    draw((cx-iw,cy)--(cx-iw,cy+h), hidden);
    draw((cx+iw,cy)--(cx+iw,cy+h), hidden);

    // Top face
    fill(shift(cx,cy+h)*xscale(ew)*yscale(eh)*unitcircle, white);
    draw(shift(cx,cy+h)*xscale(ew)*yscale(eh)*unitcircle, solid);
    fill(shift(cx,cy+h)*xscale(iw)*yscale(ih)*unitcircle, white);
    draw(shift(cx,cy+h)*xscale(iw)*yscale(ih)*unitcircle, solid);
}

// ── Oblique cone ──────────────────────────────────────
void cone(real cx, real cy, real r, real h) {
    real ew = r, eh = r*0.38;
    draw(shift(cx,cy)*xscale(ew)*yscale(eh)*arc((0,0),1,180,360), solid);
    draw(shift(cx,cy)*xscale(ew)*yscale(eh)*arc((0,0),1,0,180), hidden);
    fill((cx-ew,cy)--(cx,cy+h)--(cx+ew,cy)--cycle, white);
    draw((cx-ew,cy)--(cx,cy+h), solid);
    draw((cx+ew,cy)--(cx,cy+h), solid);
    dot((cx,cy+h), solid);
}

// ── Layout: components separated by GAP ──────────────
real BASE_R=20, BASE_H=8, BASE_T=1.5;
real FEED_R=2,  FEED_H=5;
real MID_R=6,   MID_T=1.5, MID_H=40;
real TOP_R=4,   TOP_H=20;
real GAP = 20;

real cx = 0;
real y1 = 0;                                    // (1) Base plate bottom
real y2 = BASE_H + GAP;                         // (2) Feed pin bottom
real y3 = y2 + FEED_H + GAP;                   // (3) Sleeve bottom
real y4 = y3 + MID_H + GAP;                    // (4) Cone bottom

// Assembly axis dashed line
draw((cx, y1+BASE_H/2)--(cx, y4+TOP_H), dash+linewidth(0.4pt));

// Draw parts bottom→top
cyl(cx, y1, BASE_R, BASE_H);
// Gap connector
draw((cx,BASE_H)--(cx,y2), dash);

cyl(cx, y2, FEED_R, FEED_H);
draw((cx,y2+FEED_H)--(cx,y3), dash);

hollow_cyl(cx, y3, MID_R, MID_T, MID_H);
draw((cx,y3+MID_H)--(cx,y4), dash);

cone(cx, y4, TOP_R, TOP_H);

// ── Part number balloons ──────────────────────────────
real lx = BASE_R + 8;
void balloon(string n, real bx, real by) {
    pair c = (bx, by);
    fill(circle(c, 3.5), white);
    draw(circle(c, 3.5), thin);
    label(n, c, fontsize(8pt));
}

draw((BASE_R,y1+BASE_H/2)--(lx-1,y1+BASE_H/2), thin, Arrow(4));
balloon("1", lx+2, y1+BASE_H/2);

draw((FEED_R+0.5,y2+FEED_H/2)--(lx-1,y2+FEED_H/2), thin, Arrow(4));
balloon("2", lx+2, y2+FEED_H/2);

draw((MID_R+0.5,y3+MID_H/2)--(lx-1,y3+MID_H/2), thin, Arrow(4));
balloon("3", lx+2, y3+MID_H/2);

draw((TOP_R*0.5,y4+TOP_H*0.6)--(lx-1,y4+TOP_H*0.6), thin, Arrow(4));
balloon("4", lx+2, y4+TOP_H*0.6);

// ── Title ─────────────────────────────────────────────
label("\textbf{Fig. 2 -- Exploded View}", (cx,-10), fontsize(9pt));
