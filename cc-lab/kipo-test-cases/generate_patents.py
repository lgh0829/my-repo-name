"""
KIPO 심사 테스트용 특허 명세서 PDF 생성기
6개 케이스: 난이도 낮음(2), 중간(2), 높음(2)
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
import os

# ─── 폰트 등록 ─────────────────────────────────────────────────────────────
FONT_PATH = '/tmp/NanumGothic-Regular.ttf'
pdfmetrics.registerFont(TTFont('Nanum', FONT_PATH))
pdfmetrics.registerFont(TTFont('NanumB', FONT_PATH))  # bold 대체

W, H = A4
OUT_DIR = '/Users/leegh/cc-workspace/cc-lab/kipo-test-cases'

# ─── 스타일 ─────────────────────────────────────────────────────────────────
def make_styles():
    return {
        'title': ParagraphStyle('title', fontName='Nanum', fontSize=15,
                                leading=22, spaceAfter=6,
                                textColor=colors.HexColor('#1a1a2e')),
        'h1': ParagraphStyle('h1', fontName='Nanum', fontSize=12,
                              leading=18, spaceBefore=10, spaceAfter=4,
                              textColor=colors.HexColor('#16213e')),
        'h2': ParagraphStyle('h2', fontName='Nanum', fontSize=10,
                              leading=16, spaceBefore=6, spaceAfter=2,
                              textColor=colors.HexColor('#0f3460')),
        'body': ParagraphStyle('body', fontName='Nanum', fontSize=9,
                               leading=15, spaceAfter=4),
        'claim': ParagraphStyle('claim', fontName='Nanum', fontSize=9,
                                leading=15, leftIndent=10, spaceAfter=4),
        'note': ParagraphStyle('note', fontName='Nanum', fontSize=8,
                               leading=13, textColor=colors.HexColor('#555555')),
        'fig_cap': ParagraphStyle('fig_cap', fontName='Nanum', fontSize=8,
                                  leading=12, alignment=1,
                                  textColor=colors.HexColor('#444444')),
    }

# ─── 다이어그램 Flowable 기반 클래스 ────────────────────────────────────────
class DiagramFlowable(Flowable):
    def __init__(self, width, height, draw_fn, caption=''):
        super().__init__()
        self.width = width
        self.height = height
        self.draw_fn = draw_fn
        self.caption = caption

    def draw(self):
        self.draw_fn(self.canv, self.width, self.height)


# ─── 다이어그램 그리기 함수들 ────────────────────────────────────────────────

def draw_box(c, x, y, w, h, label, sublabel='', fill=None, text_size=8):
    if fill:
        c.setFillColor(colors.HexColor(fill))
        c.rect(x, y, w, h, fill=1, stroke=1)
        c.setFillColor(colors.black)
    else:
        c.rect(x, y, w, h)
    c.setFont('Nanum', text_size)
    c.drawCentredString(x + w/2, y + h/2 + (5 if sublabel else 0), label)
    if sublabel:
        c.setFont('Nanum', 7)
        c.drawCentredString(x + w/2, y + h/2 - 8, sublabel)

def draw_arrow(c, x1, y1, x2, y2, label=''):
    c.line(x1, y1, x2, y2)
    # arrowhead
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    al = 8
    aw = 4
    c.line(x2, y2,
           x2 - al * math.cos(angle) + aw * math.sin(angle),
           y2 - al * math.sin(angle) - aw * math.cos(angle))
    c.line(x2, y2,
           x2 - al * math.cos(angle) - aw * math.sin(angle),
           y2 - al * math.sin(angle) + aw * math.cos(angle))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        c.setFont('Nanum', 7)
        c.drawCentredString(mx, my + 5, label)


# ── 1. 스마트 조명 제어 시스템 블록 다이어그램 ──────────────────────────────
def diagram_smart_lighting(c, W, H):
    c.setStrokeColor(colors.HexColor('#333333'))
    c.setFillColor(colors.black)
    c.setFont('Nanum', 9)
    c.drawCentredString(W/2, H - 20, '【도면 1】 스마트 조명 제어 시스템 블록도')

    bw, bh = 110, 40
    gap = 30
    total = 4 * bw + 3 * gap
    sx = (W - total) / 2
    cy = H / 2

    boxes = [
        ('#dce8f5', '조도 센서\n(Lux Sensor)', '실외·실내 조도 측정'),
        ('#d4edda', '마이크로컨트롤러\n(MCU)', '패턴 학습 / 제어 알고리즘'),
        ('#fff3cd', 'PWM 드라이버', '전류 듀티 사이클 조절'),
        ('#f8d7da', 'LED 조명 어레이', '가시광 출력'),
    ]

    for i, (fill, label, sub) in enumerate(boxes):
        bx = sx + i * (bw + gap)
        draw_box(c, bx, cy - bh/2, bw, bh, label.replace('\n', ' '), sub, fill, 8)
        if i < len(boxes) - 1:
            draw_arrow(c, bx + bw, cy, bx + bw + gap, cy)

    # 피드백 화살표
    c.setDash(4, 3)
    c.line(sx + 3*(bw + gap) + bw/2, cy - bh/2 - 10,
           sx + bw/2, cy - bh/2 - 10)
    draw_arrow(c, sx + bw/2, cy - bh/2 - 10, sx + bw/2, cy - bh/2)
    c.setDash()
    c.setFont('Nanum', 7)
    c.drawCentredString(W/2, cy - bh/2 - 20, '← 피드백 루프 (조도 측정값 → MCU 재입력)')

    # 범례
    legend_y = cy - bh/2 - 50
    items = [('#dce8f5', '센서'), ('#d4edda', '제어'), ('#fff3cd', '드라이버'), ('#f8d7da', '출력')]
    lx = (W - len(items) * 80) / 2
    for j, (col, name) in enumerate(items):
        c.setFillColor(colors.HexColor(col))
        c.rect(lx + j*80, legend_y, 16, 10, fill=1, stroke=1)
        c.setFillColor(colors.black)
        c.setFont('Nanum', 7)
        c.drawString(lx + j*80 + 20, legend_y + 1, name)


# ── 2. 폐열 회수형 환기 장치 단면도 ──────────────────────────────────────────
def diagram_heat_recovery(c, W, H):
    import math
    c.setFont('Nanum', 9)
    c.drawCentredString(W/2, H - 20, '【도면 2】 폐열 회수형 환기 장치 단면도')

    ox, oy = W/2 - 100, H/2 - 80
    bw, bh = 200, 160

    # 장치 외곽
    c.setStrokeColor(colors.HexColor('#555'))
    c.setLineWidth(2)
    c.rect(ox, oy, bw, bh)
    c.setLineWidth(1)

    # 열교환기 코어 (격자)
    cx, cy2 = ox + bw*0.2, oy + bh*0.2
    cw, ch = bw*0.6, bh*0.6
    c.setFillColor(colors.HexColor('#cfe2f3'))
    c.rect(cx, cy2, cw, ch, fill=1)
    c.setFillColor(colors.black)
    for k in range(1, 5):
        c.line(cx + cw*k/5, cy2, cx + cw*k/5, cy2 + ch)
        c.line(cx, cy2 + ch*k/5, cx + cw, cy2 + ch*k/5)
    c.setFont('Nanum', 8)
    c.drawCentredString(cx + cw/2, cy2 + ch/2, '열교환기 코어')

    # 급기 흐름 (왼쪽 → 오른쪽, 상단)
    for offset in [-20, 0, 20]:
        ay = oy + bh*0.75 + offset
        draw_arrow(c, ox - 40, ay, cx - 5, ay)
    c.setFont('Nanum', 8)
    c.setFillColor(colors.HexColor('#1a73e8'))
    c.drawCentredString(ox - 50, oy + bh*0.75, '외기\n급기')
    c.setFillColor(colors.black)
    for offset in [-20, 0, 20]:
        ay = oy + bh*0.75 + offset
        draw_arrow(c, cx + cw + 5, ay, ox + bw + 40, ay)
    c.setFillColor(colors.HexColor('#1a73e8'))
    c.drawCentredString(ox + bw + 55, oy + bh*0.75, '정화된\n급기')

    # 배기 흐름 (오른쪽 → 왼쪽, 하단)
    for offset in [-20, 0, 20]:
        ay = oy + bh*0.25 + offset
        draw_arrow(c, ox + bw + 40, ay, cx + cw + 5, ay)
    c.setFillColor(colors.HexColor('#e53935'))
    c.drawCentredString(ox + bw + 55, oy + bh*0.25, '실내\n배기')
    c.setFillColor(colors.black)
    for offset in [-20, 0, 20]:
        ay = oy + bh*0.25 + offset
        draw_arrow(c, cx - 5, ay, ox - 40, ay)
    c.setFillColor(colors.HexColor('#e53935'))
    c.drawCentredString(ox - 50, oy + bh*0.25, '열 회수\n후 배출')
    c.setFillColor(colors.black)

    # 열전달 표시
    c.setStrokeColor(colors.HexColor('#ff9800'))
    c.setDash(3, 3)
    c.line(cx + cw/2 - 20, cy2 + ch, cx + cw/2 - 20, cy2)
    c.line(cx + cw/2 + 20, cy2 + ch, cx + cw/2 + 20, cy2)
    c.setDash()
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.HexColor('#ff9800'))
    c.setFont('Nanum', 7)
    c.drawCentredString(cx + cw/2, cy2 - 12, '← 열전달 방향 →')
    c.setFillColor(colors.black)


# ── 3. AI 피부 진단 플로우차트 ───────────────────────────────────────────────
def diagram_skin_ai(c, W, H):
    c.setFont('Nanum', 9)
    c.drawCentredString(W/2, H - 20, '【도면 3】 AI 피부 진단·추천 처리 흐름도')

    steps = [
        ('#e8f5e9', '피부 이미지 촬영\n(카메라 모듈)', 'round'),
        ('#e3f2fd', '전처리\n(노이즈 제거·정규화)', 'rect'),
        ('#fff9c4', 'CNN 피부 분석\n(피부 타입·트러블 분류)', 'rect'),
        ('#fce4ec', '사용자 이력 DB\n조회·결합', 'rect'),
        ('#ede7f6', '"최적" 제품 추천\n생성 (추천 엔진)', 'diamond'),
        ('#e0f7fa', '추천 결과 출력\n(앱 UI / 레포트)', 'round'),
    ]

    bw, bh = 140, 38
    sx = W/2 - bw/2
    sy = H - 50
    gap = 20

    for i, (fill, label, shape) in enumerate(steps):
        y = sy - i * (bh + gap)
        c.setFillColor(colors.HexColor(fill))
        if shape == 'diamond':
            pts = [(sx + bw/2, y + bh), (sx + bw, y + bh/2),
                   (sx + bw/2, y), (sx, y + bh/2)]
            p = c.beginPath()
            p.moveTo(*pts[0])
            for pt in pts[1:]:
                p.lineTo(*pt)
            p.close()
            c.drawPath(p, fill=1, stroke=1)
        elif shape == 'round':
            c.roundRect(sx, y, bw, bh, 10, fill=1, stroke=1)
        else:
            c.rect(sx, y, bw, bh, fill=1, stroke=1)

        c.setFillColor(colors.black)
        c.setFont('Nanum', 8)
        lines = label.split('\n')
        if len(lines) == 2:
            c.drawCentredString(sx + bw/2, y + bh/2 + 4, lines[0])
            c.drawCentredString(sx + bw/2, y + bh/2 - 8, lines[1])
        else:
            c.drawCentredString(sx + bw/2, y + bh/2, lines[0])

        if i < len(steps) - 1:
            next_y = y - gap
            draw_arrow(c, sx + bw/2, y, sx + bw/2, next_y)

    # 주석: 불명확 용어 표시
    diamond_y = sy - 4*(bh + gap)
    c.setStrokeColor(colors.HexColor('#e53935'))
    c.setFillColor(colors.HexColor('#e53935'))
    c.setFont('Nanum', 7)
    c.drawString(sx + bw + 8, diamond_y + bh/2, '⚠ "최적" — 불명확 용어')
    c.line(sx + bw, diamond_y + bh/2, sx + bw + 6, diamond_y + bh/2)
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.black)


# ── 4. 블록체인 의료 기록 네트워크도 ────────────────────────────────────────
def diagram_blockchain(c, W, H):
    import math
    c.setFont('Nanum', 9)
    c.drawCentredString(W/2, H - 20, '【도면 4】 블록체인 의료 기록 공유 시스템 네트워크도')

    cx, cy2 = W/2, H/2

    # 중앙 블록체인 노드
    c.setFillColor(colors.HexColor('#fff3cd'))
    c.circle(cx, cy2, 35, fill=1)
    c.setFillColor(colors.black)
    c.setFont('Nanum', 8)
    c.drawCentredString(cx, cy2 + 5, '블록체인')
    c.drawCentredString(cx, cy2 - 8, '분산 원장')

    # 참여 노드 6개
    nodes = [
        ('병원 A', '#dce8f5', 0),
        ('병원 B', '#dce8f5', 60),
        ('약국', '#d4edda', 120),
        ('보험사', '#f8d7da', 180),
        ('병원 C', '#dce8f5', 240),
        ('연구소', '#ede7f6', 300),
    ]
    r = 110
    for label, fill, angle_deg in nodes:
        angle = math.radians(angle_deg)
        nx = cx + r * math.cos(angle)
        ny = cy2 + r * math.sin(angle)
        c.setFillColor(colors.HexColor(fill))
        c.roundRect(nx - 35, ny - 18, 70, 36, 6, fill=1, stroke=1)
        c.setFillColor(colors.black)
        c.setFont('Nanum', 8)
        c.drawCentredString(nx, ny + 4, label)

        # 연결선
        ex = cx + 35 * math.cos(angle)
        ey = cy2 + 35 * math.sin(angle)
        lx = nx - 35 * math.cos(angle)
        ly = ny - 35 * math.sin(angle)
        c.setDash(3, 2)
        c.line(ex, ey, lx, ly)
        c.setDash()

    # 스마트 컨트랙트 표시
    c.setFillColor(colors.HexColor('#0f3460'))
    c.setFont('Nanum', 7)
    c.setFillColor(colors.black)
    c.drawCentredString(cx, cy2 - 70, '← 스마트 컨트랙트 기반 접근 제어 →')


# ── 5. 양자 얽힘 통신 개념도 ─────────────────────────────────────────────────
def diagram_quantum(c, W, H):
    import math
    c.setFont('Nanum', 9)
    c.drawCentredString(W/2, H - 20, '【도면 5】 양자 얽힘 기반 통신 개념도')

    sy = H/2 + 20

    # 송신자 Alice
    draw_box(c, 30, sy - 30, 80, 60, 'Alice\n(송신자)', '측정·인코딩', '#dce8f5', 8)

    # 수신자 Bob
    draw_box(c, W - 110, sy - 30, 80, 60, 'Bob\n(수신자)', '측정·디코딩', '#d4edda', 8)

    # 얽힘 쌍 생성기
    draw_box(c, W/2 - 50, sy - 25, 100, 50, '얽힘 쌍\n생성기', 'EPR 쌍 분배', '#fff3cd', 8)

    # 얽힘 쌍 분배선
    c.setStrokeColor(colors.HexColor('#8e24aa'))
    c.setLineWidth(1.5)
    c.setDash(5, 3)
    c.line(110, sy, W/2 - 50, sy)
    c.line(W/2 + 50, sy, W - 110, sy)
    c.setDash()
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)

    # 고전 채널
    c.setStrokeColor(colors.HexColor('#1565c0'))
    c.line(110, sy + 50, W - 110, sy + 50)
    draw_arrow(c, W/2, sy + 50, W/2 + 1, sy + 50)
    c.setFont('Nanum', 7)
    c.setFillColor(colors.HexColor('#1565c0'))
    c.drawCentredString(W/2, sy + 60, '고전 채널 (동기화 정보 전송)')
    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)

    # 레이블
    c.setFillColor(colors.HexColor('#8e24aa'))
    c.setFont('Nanum', 7)
    c.drawCentredString(W/2, sy - 40, '얽힘 쌍 분배 (양자 채널)')
    c.setFillColor(colors.black)

    # 경고 박스
    c.setStrokeColor(colors.HexColor('#e53935'))
    c.setFillColor(colors.HexColor('#ffebee'))
    c.roundRect(W/2 - 90, sy - 90, 180, 30, 5, fill=1, stroke=1)
    c.setFillColor(colors.HexColor('#e53935'))
    c.setFont('Nanum', 7)
    c.drawCentredString(W/2, sy - 72, '⚠ 실시 예: 상온·원거리 얽힘 유지 방법 미기재')
    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)


# ── 6. 감정 인식 광고 생성 아키텍처 ──────────────────────────────────────────
def diagram_emotion_ad(c, W, H):
    c.setFont('Nanum', 9)
    c.drawCentredString(W/2, H - 20, '【도면 6】 감정 인식 기반 광고 자동 생성 시스템 아키텍처')

    # 레이어 구성
    layers = [
        ('#e3f2fd', '입력 레이어', [('카메라 모듈', 80, 30), ('마이크', 80, 30)]),
        ('#e8f5e9', '인식 레이어', [('얼굴 표정 분석\n(CNN)', 100, 40), ('음성 감정 분석\n(RNN)', 100, 40)]),
        ('#fff9c4', '추론 레이어', [('감정 융합 모델\n(Multi-modal)', 120, 40)]),
        ('#fce4ec', '생성 레이어', [('광고 카피 생성\n(LLM)', 100, 40), ('이미지 생성\n(GAN)', 100, 40)]),
        ('#ede7f6', '출력 레이어', [('실시간 광고\n디스플레이', 120, 40)]),
    ]

    lx = 20
    ly = H - 50
    gap_y = 20
    gap_x = 15

    for layer_fill, layer_name, boxes in layers:
        total_w = sum(bw + gap_x for bw, bh in [b[1:] for b in boxes]) - gap_x
        layer_h = max(bh for _, bw, bh in boxes)
        layer_w = W - 40

        # 레이어 배경
        c.setFillColor(colors.HexColor(layer_fill))
        c.setStrokeColor(colors.HexColor('#aaaaaa'))
        c.roundRect(lx, ly - layer_h, layer_w, layer_h, 5, fill=1, stroke=1)
        c.setFillColor(colors.HexColor('#555555'))
        c.setFont('Nanum', 7)
        c.drawString(lx + 5, ly - 10, layer_name)

        # 박스들
        box_sx = (layer_w - total_w) / 2 + lx
        bx = box_sx
        for label, bw, bh in boxes:
            by = ly - layer_h/2 - bh/2
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.HexColor('#888888'))
            c.roundRect(bx, by, bw, bh, 4, fill=1, stroke=1)
            c.setFillColor(colors.black)
            c.setFont('Nanum', 7)
            lines = label.split('\n')
            if len(lines) == 2:
                c.drawCentredString(bx + bw/2, by + bh/2 + 4, lines[0])
                c.drawCentredString(bx + bw/2, by + bh/2 - 6, lines[1])
            else:
                c.drawCentredString(bx + bw/2, by + bh/2, lines[0])
            bx += bw + gap_x

        ly -= layer_h + gap_y
        if layers.index((layer_fill, layer_name, boxes)) < len(layers) - 1:
            draw_arrow(c, lx + layer_w/2, ly + gap_y, lx + layer_w/2, ly)

    # 과도한 청구항 경고
    c.setStrokeColor(colors.HexColor('#e53935'))
    c.setFillColor(colors.HexColor('#ffebee'))
    c.roundRect(W - 150, H - 50, 135, 50, 5, fill=1, stroke=1)
    c.setFillColor(colors.HexColor('#e53935'))
    c.setFont('Nanum', 7)
    c.drawCentredString(W - 82, H - 20, '⚠ 청구항 범위 과도')
    c.drawCentredString(W - 82, H - 33, '"모든 감정 상태에 대해"')
    c.drawCentredString(W - 82, H - 46, '"임의의 광고 유형" → 불명확')
    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)


# ─── 특허 명세서 데이터 ──────────────────────────────────────────────────────

PATENTS = [
    {
        'filename': '01_smart_lighting_system.pdf',
        'case': '1',
        'difficulty': '★☆☆ 낮음',
        'title': '조도 센서와 머신러닝을 이용한 자동 밝기 조절 스마트 조명 제어 시스템',
        'tech_field': '전기·전자, 인공지능(기계 학습)',
        'ipc': 'H05B 47/10, G06N 20/00',
        'background': (
            '기존 조명 시스템은 시간 기반 타이머 또는 단순 수동 스위치에 의존하여 에너지 낭비가 심하다. '
            '특히 재실자의 활동 패턴이나 외부 자연광 변화를 실시간으로 반영하지 못해, 불필요한 전력 소모가 발생한다. '
            '일부 시스템은 조도 센서를 탑재하나 단순 임계값 비교 방식이어서 사용자의 선호 밝기를 학습하지 못한다.'
        ),
        'summary': (
            '본 발명은 실내외 조도 센서로 측정한 조도 값과 재실자의 과거 조명 조작 이력을 기반으로 '
            '머신러닝 모델이 최적 밝기를 예측하고, PWM 신호를 이용해 LED 조명의 밝기를 자동 조절하는 시스템에 관한 것이다. '
            '마이크로컨트롤러(MCU)는 측정 주기마다 조도 데이터를 수집하고, 내장된 k-NN 또는 선형 회귀 모델로 '
            '목표 밝기를 산출한 후 PWM 드라이버로 LED 전류를 제어한다.'
        ),
        'claims': [
            '청구항 1. 실내 조도를 측정하는 제1 조도 센서; 실외 조도를 측정하는 제2 조도 센서; '
            '상기 제1 및 제2 조도 센서로부터 수신한 조도 데이터와 사용자 조작 이력을 이용하여 목표 밝기를 산출하는 마이크로컨트롤러(MCU); '
            '상기 MCU의 출력 신호에 따라 PWM 듀티 사이클을 변경하여 LED 전류를 제어하는 PWM 드라이버; 및 '
            '상기 PWM 드라이버에 의해 구동되는 LED 조명 어레이;를 포함하는 스마트 조명 제어 시스템.',
            '청구항 2. 제1항에 있어서, 상기 MCU는 k-최근접 이웃(k-NN) 알고리즘 또는 선형 회귀 모델 중 하나를 이용하여 '
            '목표 밝기를 산출하는 것을 특징으로 하는 스마트 조명 제어 시스템.',
            '청구항 3. 제1항에 있어서, 상기 시스템은 실내 재실 여부를 감지하는 PIR 센서를 더 포함하고, '
            '재실자가 없는 경우 LED 조명 어레이를 소등하는 것을 특징으로 하는 스마트 조명 제어 시스템.',
        ],
        'drawings': [('도 1', '스마트 조명 제어 시스템 전체 블록도')],
        'diagram_fn': diagram_smart_lighting,
    },
    {
        'filename': '02_heat_recovery_ventilator.pdf',
        'case': '2',
        'difficulty': '★☆☆ 낮음',
        'title': '대향류 열교환기를 구비한 폐열 회수형 건물 환기 장치',
        'tech_field': '기계공학, 건물 설비, 공조(HVAC)',
        'ipc': 'F24F 12/00, F28D 9/00',
        'background': (
            '현대 건물은 기밀성이 높아져 자연 환기가 어려워졌으며, 강제 환기 시 실내 열이 그대로 외부로 배출되어 '
            '냉난방 에너지 손실이 크다. 단순 환기팬 방식은 환기량은 확보되나 에너지 효율이 낮아 '
            '열 회수 없이는 난방 부하가 크게 증가한다. '
            '기존 열교환형 환기장치는 병류 방식이어서 열전달 효율이 60~70% 수준에 머물고 있다.'
        ),
        'summary': (
            '본 발명은 급기와 배기가 대향류(counter-flow) 방향으로 흐르도록 설계된 열교환기 코어를 채용하여 '
            '열 회수 효율을 85% 이상으로 높인 환기 장치에 관한 것이다. '
            '급기팬이 외기를 흡입하면 열교환기 코어를 통과하면서 실내 배기열을 흡수하고, '
            '배기팬은 실내 오염 공기를 코어를 통해 외부로 배출하는 동시에 열을 급기 쪽으로 전달한다. '
            '알루미늄 박판 핀 구조의 코어는 접촉 면적을 최대화하여 열전달 계수를 향상시킨다.'
        ),
        'claims': [
            '청구항 1. 외기를 실내로 공급하는 급기 유로; 실내 공기를 외부로 배출하는 배기 유로; '
            '상기 급기 유로와 배기 유로가 서로 대향류를 이루도록 배치된 알루미늄 박판 핀 열교환기 코어; '
            '상기 급기 유로 내에 설치된 급기팬; 및 상기 배기 유로 내에 설치된 배기팬;을 포함하며, '
            '열 회수 효율이 85% 이상인 폐열 회수형 환기 장치.',
            '청구항 2. 제1항에 있어서, 상기 열교환기 코어의 핀 피치가 1.5 mm 이상 3.0 mm 이하인 것을 특징으로 하는 환기 장치.',
            '청구항 3. 제1항에 있어서, 상기 급기 유로의 입구에 PM2.5 필터가 설치된 것을 특징으로 하는 환기 장치.',
        ],
        'drawings': [('도 1', '대향류 열교환기 환기 장치 단면 구조도')],
        'diagram_fn': diagram_heat_recovery,
    },
    {
        'filename': '03_ai_skin_diagnosis.pdf',
        'case': '3',
        'difficulty': '★★☆ 중간',
        'title': '인공지능 기반 피부 상태 진단 및 최적 화장품 추천 방법과 시스템',
        'tech_field': '소프트웨어, 바이오·미용, 컴퓨터 비전',
        'ipc': 'G06V 40/16, G06N 3/08, A61B 5/00',
        'background': (
            '소비자는 자신의 피부 타입과 상태에 맞는 화장품 선택에 어려움을 겪고 있으며, '
            '오프라인 상담은 시간·공간적 제약이 크다. 기존 앱 기반 피부 진단은 설문 방식에 의존하여 '
            '객관적 측정값이 부족하고 개인화 정도가 낮다. '
            '딥러닝 기반 이미지 분석이 발전하였으나, 피부 분석에 특화된 경량 모델과 추천 알고리즘의 결합 사례는 제한적이다.'
        ),
        'summary': (
            '본 발명은 스마트폰 카메라로 촬영한 얼굴 이미지를 CNN 기반 피부 분석 모델에 입력하여 '
            '피부 타입(건성·지성·복합성·민감성)과 트러블 유형(여드름·색소침착·주름)을 분류하고, '
            '사용자 이력 데이터와 결합하여 최적화된 화장품을 추천하는 방법 및 시스템에 관한 것이다. '
            '추천 엔진은 협업 필터링과 콘텐츠 기반 필터링을 결합한 하이브리드 방식을 채용하며, '
            '효과적인 성분 매칭을 수행한다.'
        ),
        'claims': [
            '청구항 1. 사용자 피부 이미지를 획득하는 단계; 상기 이미지를 전처리하는 단계; '
            'CNN 모델로 피부 타입 및 트러블 유형을 분류하는 단계; '
            '사용자 이력 데이터와 결합하여 최적화된 화장품을 추천하는 단계; 및 '
            '추천 결과를 사용자 인터페이스에 출력하는 단계;를 포함하는 피부 진단 및 추천 방법.',
            '청구항 2. 제1항에 있어서, 상기 추천 단계는 협업 필터링 및 콘텐츠 기반 필터링을 결합한 '
            '하이브리드 방식으로 효과적인 화장품을 선정하는 것을 특징으로 하는 방법. '
            '※ 심사 주목: "최적화된", "효과적인" 등 불명확 용어 포함.',
            '청구항 3. 제1항의 방법을 실행하는 프로그램을 기록한 컴퓨터 판독 가능 기록매체.',
        ],
        'drawings': [('도 1', 'AI 피부 진단 및 추천 처리 흐름도')],
        'diagram_fn': diagram_skin_ai,
    },
    {
        'filename': '04_blockchain_medical_records.pdf',
        'case': '4',
        'difficulty': '★★☆ 중간',
        'title': '프라이빗 블록체인 기반 의료 기록 공유 및 접근 제어 시스템',
        'tech_field': 'IT, 의료정보학, 분산 시스템',
        'ipc': 'G16H 10/60, H04L 9/32, G06F 21/62',
        'background': (
            '병원 간 의료 기록 공유는 중앙 집중식 서버에 의존하여 단일 장애점(SPoF)과 해킹 위험이 존재한다. '
            '환자 동의 없이 의료 정보가 제3자에게 노출될 가능성이 있으며, '
            '기관별 데이터 포맷이 달라 상호운용성이 낮다. '
            '블록체인 기술은 데이터 무결성과 불변성을 보장하나, '
            '의료 특수성(대용량 이미지, 실시간 조회) 요구사항을 동시에 만족하는 설계가 필요하다.'
        ),
        'summary': (
            '본 발명은 허가형(permissioned) 블록체인 네트워크를 의료 기관에 배포하고, '
            '스마트 컨트랙트로 환자의 동의에 기반한 접근 권한을 자동 관리하는 시스템에 관한 것이다. '
            '의료 기록 원문은 분산 파일 시스템(IPFS)에 저장하고 해시값만 체인에 기록하여 '
            '성능과 프라이버시를 동시에 확보한다. '
            '각 기관은 검증자 노드로서 합의 알고리즘(PBFT)에 참여하며, '
            '권한 없는 접근 시도는 스마트 컨트랙트가 자동 거부한다.'
        ),
        'claims': [
            '청구항 1. 복수의 의료 기관이 검증자 노드로 참여하는 허가형 블록체인 네트워크; '
            '환자 동의 정보 및 접근 권한을 관리하는 스마트 컨트랙트; '
            '의료 기록 원문을 저장하고 콘텐츠 주소 해시를 반환하는 분산 파일 시스템; 및 '
            '상기 해시를 블록체인에 기록·조회하는 의료 기록 관리 모듈;을 포함하는 의료 기록 공유 시스템.',
            '청구항 2. 제1항에 있어서, 상기 합의 알고리즘은 PBFT(Practical Byzantine Fault Tolerance)인 것을 특징으로 하는 시스템.',
            '청구항 3. 제1항에 있어서, 환자 동의 철회 시 스마트 컨트랙트가 해당 기관의 조회 권한을 즉시 무효화하는 것을 특징으로 하는 시스템.',
        ],
        'drawings': [('도 1', '블록체인 의료 기록 공유 시스템 네트워크 구성도')],
        'diagram_fn': diagram_blockchain,
    },
    {
        'filename': '05_quantum_entanglement_comm.pdf',
        'case': '5',
        'difficulty': '★★★ 높음',
        'title': '양자 얽힘 상태를 이용한 도청 불가 무선 통신 방법',
        'tech_field': '양자 통신, 양자 암호, 물리학',
        'ipc': 'H04B 10/70, G06N 10/00, H04L 9/08',
        'background': (
            '기존 공개키 암호화 방식은 양자 컴퓨터의 쇼어 알고리즘에 의해 해독될 위험이 있어 '
            '장기적 보안성이 위협받고 있다. 양자 키 분배(QKD) 기술이 연구되고 있으나 '
            '광섬유 기반으로 전송 거리가 제한되고, 중계기 없이는 수백 km 이상 불가능하다. '
            '무선(RF) 채널에서 양자 얽힘을 유지하며 정보를 전달하는 방법은 아직 실용화 단계에 이르지 못했다.'
        ),
        'summary': (
            '본 발명은 얽힘 광자쌍(EPR 쌍)을 생성하여 송신자(Alice)와 수신자(Bob)에게 각각 분배한 후, '
            '양자 측정 결과의 상관성을 이용해 비밀 키를 공유하고 도청 여부를 물리 법칙으로 탐지하는 '
            '무선 통신 방법에 관한 것이다. '
            'Bell 부등식 위반 여부를 측정하여 채널 보안성을 검증하고, '
            '고전 채널로 동기화 정보를 교환하여 양자 키를 확립한다.'
        ),
        'claims': [
            '청구항 1. 얽힘 광자쌍을 생성하는 EPR 쌍 생성기; '
            '상기 EPR 쌍의 일 광자를 수신하여 측정하는 Alice 단말; '
            '상기 EPR 쌍의 타 광자를 수신하여 측정하는 Bob 단말; 및 '
            '상기 Alice 단말과 Bob 단말이 고전 채널로 측정 기저 정보를 교환하여 비밀 키를 확립하는 프로토콜 처리부;를 포함하는 양자 통신 시스템. '
            '※ 심사 주목: 상온·원거리 무선 환경에서의 얽힘 유지 방법, 구체적 실시 예 미기재.',
            '청구항 2. 제1항에 있어서, 도청 탐지를 위해 Bell 부등식 위반 여부를 주기적으로 검증하는 보안 검증부를 더 포함하는 양자 통신 시스템.',
            '청구항 3. 제1항에 있어서, 상기 EPR 쌍 생성기는 자발적 매개변수 하향 변환(SPDC)을 이용하는 것을 특징으로 하는 양자 통신 시스템.',
        ],
        'drawings': [('도 1', '양자 얽힘 기반 무선 통신 개념도')],
        'diagram_fn': diagram_quantum,
    },
    {
        'filename': '06_emotion_ad_generation.pdf',
        'case': '6',
        'difficulty': '★★★ 높음',
        'title': '실시간 감정 인식 기반 개인화 광고 자동 생성 시스템 및 방법',
        'tech_field': '인공지능, 마케팅 기술, 컴퓨터 비전, 자연어 처리',
        'ipc': 'G06V 40/16, G06F 40/56, G06Q 30/02',
        'background': (
            '디지털 광고 시장에서 클릭률(CTR)을 높이기 위한 개인화 광고가 증가하고 있으나, '
            '대부분은 사용자의 검색·구매 이력에만 의존하여 현재 감정 상태를 반영하지 못한다. '
            '감정에 맞는 광고가 구매 의도를 높인다는 연구 결과가 있으나, '
            '실시간 감정 인식과 광고 콘텐츠 생성을 통합한 시스템은 부재하다.'
        ),
        'summary': (
            '본 발명은 카메라와 마이크로 실시간 사용자 감정을 인식하고, '
            '대형 언어 모델(LLM)로 광고 카피를 생성하며, 생성적 적대 신경망(GAN)으로 광고 이미지를 합성하여 '
            '감정 상태에 최적화된 광고를 실시간으로 노출하는 시스템에 관한 것이다. '
            '청구항은 "모든 감정 상태"와 "임의의 광고 유형"을 포괄하도록 광범위하게 작성하였다.'
        ),
        'claims': [
            '청구항 1. 사용자의 표정 또는 음성 중 하나 이상으로부터 감정 상태를 인식하는 감정 인식부; '
            '상기 감정 상태에 기초하여 광고 카피를 생성하는 텍스트 생성부; '
            '상기 감정 상태에 기초하여 광고 이미지를 합성하는 이미지 생성부; 및 '
            '생성된 광고 콘텐츠를 출력하는 표시부;를 포함하며, '
            '모든 감정 상태 및 임의의 광고 유형에 적용 가능한 광고 자동 생성 시스템. '
            '※ 심사 주목: "모든 감정 상태", "임의의 광고 유형" 등 과도하게 넓은 청구 범위.',
            '청구항 2. 제1항에 있어서, 상기 감정 인식부는 CNN 기반 표정 분류 모델과 RNN 기반 음성 감정 분석 모델을 융합하는 것을 특징으로 하는 시스템.',
            '청구항 3. 제1항에 있어서, 개인정보 보호를 위해 감정 인식 데이터를 세션 종료 후 즉시 삭제하는 것을 특징으로 하는 시스템.',
        ],
        'drawings': [('도 1', '감정 인식 기반 광고 자동 생성 시스템 아키텍처')],
        'diagram_fn': diagram_emotion_ad,
    },
]


# ─── PDF 생성 메인 함수 ───────────────────────────────────────────────────────
def generate_patent_pdf(patent):
    styles = make_styles()
    filepath = os.path.join(OUT_DIR, patent['filename'])
    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    story = []

    # ── 표지 정보 ──────────────────────────────────────────────────────────────
    story.append(Paragraph(f'특허 명세서 (테스트 케이스 {patent["case"]})', styles['h2']))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#16213e')))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f'난이도: {patent["difficulty"]}', styles['note']))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f'<b>발명의 명칭:</b> {patent["title"]}', styles['title']))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f'<b>기술분야:</b> {patent["tech_field"]}', styles['h2']))
    story.append(Paragraph(f'<b>IPC 분류:</b> {patent["ipc"]}', styles['note']))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 8))

    # ── 배경기술 ───────────────────────────────────────────────────────────────
    story.append(Paragraph('배경기술', styles['h1']))
    story.append(Paragraph(patent['background'], styles['body']))
    story.append(Spacer(1, 8))

    # ── 발명의 내용 ────────────────────────────────────────────────────────────
    story.append(Paragraph('발명의 내용', styles['h1']))
    story.append(Paragraph(patent['summary'], styles['body']))
    story.append(Spacer(1, 8))

    # ── 청구항 ─────────────────────────────────────────────────────────────────
    story.append(Paragraph('청구범위', styles['h1']))
    for claim in patent['claims']:
        story.append(Paragraph(claim, styles['claim']))
        story.append(Spacer(1, 4))

    # ── 도면의 간단한 설명 ─────────────────────────────────────────────────────
    story.append(Spacer(1, 8))
    story.append(Paragraph('도면의 간단한 설명', styles['h1']))
    for fig_id, fig_desc in patent['drawings']:
        story.append(Paragraph(f'{fig_id}: {fig_desc}', styles['body']))

    # ── 다이어그램 페이지 ──────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph('도면', styles['h1']))
    story.append(Spacer(1, 8))

    dw = 14 * cm
    dh = 16 * cm
    diagram = DiagramFlowable(dw, dh, patent['diagram_fn'])
    story.append(diagram)

    # 도면 캡션
    story.append(Spacer(1, 6))
    for fig_id, fig_desc in patent['drawings']:
        story.append(Paragraph(f'{fig_id}. {fig_desc}', styles['fig_cap']))

    doc.build(story)
    return filepath


# ─── 실행 ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    for i, patent in enumerate(PATENTS, 1):
        path = generate_patent_pdf(patent)
        print(f'[{i}/6] 생성 완료: {os.path.basename(path)}')
    print(f'\n출력 디렉토리: {OUT_DIR}')
