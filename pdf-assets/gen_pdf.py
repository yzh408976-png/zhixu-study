# -*- coding: utf-8 -*-
import os, sys, io
BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.dirname(BASE)
PDF_PATH = os.path.join(OUT_DIR, u'云帆-参赛作品应用方案.pdf')
CH1 = os.path.join(BASE, 'chart_energy.png')
CH2 = os.path.join(BASE, 'chart_market.png')

# ---------------- matplotlib charts ----------------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def setup_cjk():
    import matplotlib.font_manager as fm
    names = [f.name for f in fm.fontManager.ttflist]
    for n in ['Microsoft YaHei', 'SimHei', 'SimSun']:
        if n in names:
            plt.rcParams['font.sans-serif'] = [n] + plt.rcParams['font.sans-serif']
            return n
    return None
setup_cjk()
plt.rcParams['axes.unicode_minus'] = False

def chart_energy():
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(9.4, 4.7), sharex=True,
        gridspec_kw={'height_ratios': [2.1, 1.0], 'hspace': 0.10})
    t = np.linspace(6, 23.3, 600)
    e = 3.0 + 4.7*np.exp(-((t-10.0)**2)/3.2) + 2.6*np.exp(-((t-19.6)**2)/4.6) - 1.5*np.exp(-((t-14.2)**2)/1.1)
    e = np.clip(e, 0.4, 10)
    ax1.plot(t, e, color='#A22D12', lw=2.2)
    ax1.fill_between(t, 0, e, color='#C7391B', alpha=0.10)
    ax1.set_ylabel('预估精力（0–10）', fontsize=10)
    ax1.set_ylim(0, 11)
    ax1.set_yticks(range(0, 11, 2))
    ax1.annotate('精力峰值\n（攻坚块对齐此处）', xy=(10, 9.9), xytext=(12.3, 9.6),
                 fontsize=9, color='#A22D12',
                 arrowprops=dict(arrowstyle='->', color='#A22D12', lw=1.2))
    ax1.annotate('午后低谷\n（安排轻量自测）', xy=(14.2, 3.4), xytext=(15.8, 1.2),
                 fontsize=9, color='#5A6B8C',
                 arrowprops=dict(arrowstyle='->', color='#5A6B8C', lw=1.0))
    for s in ['top', 'right']:
        ax1.spines[s].set_visible(False)

    blocks = [
        (8.0, 0.92, '#2F6B5E', '首胜开场'),
        (9.0, 2.10, '#C7391B', '峰值攻坚'),
        (12.0, 1.0, '#B7B2A6', '午餐休整'),
        (14.0, 0.92, '#3A5A8C', '检索自测'),
        (16.0, 1.60, '#9A7B24', '交错练习'),
        (19.0, 0.92, '#3A5A8C', '间隔复习'),
        (21.5, 0.55, '#2F6B5E', '悬念收尾'),
    ]
    for (st, du, c, lab) in blocks:
        ax2.broken_barh([(st, du)], (0.42, 0.5), facecolors=c, alpha=0.92)
        ax2.text(st + du/2.0, 1.10, lab, ha='center', va='bottom', fontsize=8.6, color='#33302A')
    ax2.set_ylim(0, 1.75)
    ax2.set_yticks([])
    ax2.set_ylabel('任务块', fontsize=10)
    ax2.set_xlim(6, 23.3)
    ax2.set_xticks(range(6, 24, 2))
    ax2.set_xticklabels(['%02d:00' % h for h in range(6, 24, 2)], fontsize=9)
    for s in ['top', 'right', 'left']:
        ax2.spines[s].set_visible(False)
    fig.savefig(CH1, dpi=150, bbox_inches='tight')
    plt.close(fig)

def chart_market():
    cats = ['2024 考研\n报名', '2025 考研\n报名', '2026 考研\n报名', '2026 国考\n过审人数']
    vals = [438, 388, 343, 371.8]
    colors = ['#7FA89B', '#578876', '#2F6B5E', '#C7391B']
    fig, ax = plt.subplots(figsize=(8.8, 3.4))
    bars = ax.bar(cats, vals, color=colors, width=0.56)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v + 7, ('%.1f' % v if v != int(v) else '%d' % v),
                ha='center', fontsize=10.5, color='#33302A', fontweight='bold')
    ax.set_ylabel('人数（万人）', fontsize=10)
    ax.set_ylim(0, 495)
    ax.grid(axis='y', linestyle='--', alpha=0.35)
    ax.set_axisbelow(True)
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=10)
    fig.savefig(CH2, dpi=150, bbox_inches='tight')
    plt.close(fig)

chart_energy()
chart_market()

# ---------------- reportlab document ----------------
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Image, PageBreak, NextPageTemplate,
                                KeepTogether)
from reportlab.platypus.flowables import HRFlowable
from reportlab.platypus.tableofcontents import TableOfContents

pdfmetrics.registerFont(TTFont('CJK', 'C:/Windows/Fonts/msyh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('CJK-Bold', 'C:/Windows/Fonts/msyhbd.ttc', subfontIndex=0))

PAGE_W, PAGE_H = A4
ML = MR = 20*mm
MT = 17*mm
MB = 19*mm
CW = PAGE_W - ML - MR

C_PRI = HexColor('#A22D12')
C_ACC = HexColor('#2F6B5E')
C_INK = HexColor('#33302A')
C_SOFT = HexColor('#6B655A')
C_LINE = HexColor('#E2D8C3')
C_PAPER = HexColor('#FAF6EC')

S = {
    'CoverKicker': ParagraphStyle('CoverKicker', fontName='CJK', fontSize=11, leading=16,
                                  textColor=C_SOFT, alignment=TA_CENTER, wordWrap='CJK'),
    'CoverTitle': ParagraphStyle('CoverTitle', fontName='CJK-Bold', fontSize=46, leading=58,
                                 textColor=C_PRI, alignment=TA_CENTER, wordWrap='CJK'),
    'CoverSub': ParagraphStyle('CoverSub', fontName='CJK-Bold', fontSize=19, leading=26,
                               textColor=C_INK, alignment=TA_CENTER, wordWrap='CJK'),
    'CoverSlogan': ParagraphStyle('CoverSlogan', fontName='CJK', fontSize=13, leading=20,
                                  textColor=C_ACC, alignment=TA_CENTER, wordWrap='CJK'),
    'H1': ParagraphStyle('H1', fontName='CJK-Bold', fontSize=16, leading=22,
                         textColor=C_PRI, spaceBefore=14, spaceAfter=4, wordWrap='CJK'),
    'H2': ParagraphStyle('H2', fontName='CJK-Bold', fontSize=12.5, leading=18,
                         textColor=C_ACC, spaceBefore=10, spaceAfter=4, wordWrap='CJK'),
    'Body': ParagraphStyle('Body', fontName='CJK', fontSize=10.5, leading=17.5,
                           textColor=C_INK, spaceBefore=0, spaceAfter=7,
                           alignment=TA_JUSTIFY, wordWrap='CJK'),
    'BodyTight': ParagraphStyle('BodyTight', fontName='CJK', fontSize=10.5, leading=17,
                                textColor=C_INK, spaceBefore=0, spaceAfter=3,
                                alignment=TA_JUSTIFY, wordWrap='CJK'),
    'Caption': ParagraphStyle('Caption', fontName='CJK', fontSize=8.8, leading=13,
                              textColor=C_SOFT, alignment=TA_CENTER, spaceBefore=4,
                              spaceAfter=10, wordWrap='CJK'),
    'Cell': ParagraphStyle('Cell', fontName='CJK', fontSize=9.3, leading=13.5,
                           textColor=C_INK, wordWrap='CJK'),
    'CellHead': ParagraphStyle('CellHead', fontName='CJK-Bold', fontSize=9.6, leading=13.5,
                               textColor=white, wordWrap='CJK'),
    'SrcTitle': ParagraphStyle('SrcTitle', fontName='CJK-Bold', fontSize=9.5, leading=14,
                               textColor=C_SOFT, spaceBefore=10, spaceAfter=3, wordWrap='CJK'),
    'Src': ParagraphStyle('Src', fontName='CJK', fontSize=8.6, leading=13,
                          textColor=C_SOFT, spaceAfter=1, wordWrap='CJK'),
    'TOCTitle': ParagraphStyle('TOCTitle', fontName='CJK-Bold', fontSize=18, leading=24,
                               textColor=C_PRI, spaceAfter=14, wordWrap='CJK'),
}

class DocT(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            sn = flowable.style.name
            if sn == 'H1':
                self.notify('TOCEntry', (0, flowable.getPlainText(), self.page))
            elif sn == 'H2':
                self.notify('TOCEntry', (1, flowable.getPlainText(), self.page))

def on_main(canv, doc):
    canv.saveState()
    canv.setStrokeColor(C_LINE)
    canv.setLineWidth(0.6)
    canv.line(ML, 13.5*mm, PAGE_W - MR, 13.5*mm)
    canv.setFont('CJK', 8)
    canv.setFillColor(C_SOFT)
    canv.drawString(ML, 9.5*mm, u'云帆 · AI 学习领航引擎 — iCAN 参赛作品应用方案')
    canv.drawRightString(PAGE_W - MR, 9.5*mm, u'第 %d 页' % doc.page)
    canv.restoreState()

doc = DocT(PDF_PATH, pagesize=A4,
           leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
           title=u'云帆 · AI 学习领航引擎 — 参赛作品应用方案',
           author=u'云帆项目组')
frame_cover = Frame(ML, MB, CW, PAGE_H - MT - MB, id='cover')
frame_main = Frame(ML, MB, CW, PAGE_H - MT - MB, id='main')
doc.addPageTemplates([
    PageTemplate(id='Cover', frames=[frame_cover]),
    PageTemplate(id='Main', frames=[frame_main], onPage=on_main),
])

story = []

def H1(txt):
    story.append(Paragraph(txt, S['H1']))
    story.append(HRFlowable(width='26%', thickness=2.2, color=C_PRI, spaceBefore=0, spaceAfter=8, hAlign='LEFT'))

def H2(txt):
    story.append(Paragraph(txt, S['H2']))

def P(txt, style='Body'):
    story.append(Paragraph(txt, S[style]))

def TBL(data, colw, header=True):
    rows = []
    for ri, row in enumerate(data):
        cells = []
        for c in row:
            if isinstance(c, Paragraph):
                cells.append(c)
            else:
                cells.append(Paragraph(c, S['CellHead'] if (header and ri == 0) else S['Cell']))
        rows.append(cells)
    t = Table(rows, colWidths=colw, repeatRows=1 if header else 0)
    style = [
        ('FONTNAME', (0, 0), (-1, -1), 'CJK'),
        ('FONTSIZE', (0, 0), (-1, -1), 9.3),
        ('LEADING', (0, 0), (-1, -1), 13.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_PAPER, white]),
        ('GRID', (0, 0), (-1, -1), 0.5, C_LINE),
    ]
    if header:
        style += [('BACKGROUND', (0, 0), (-1, 0), C_PRI)]
    t.setStyle(TableStyle(style))
    return t

def IMG(path, w_ratio=None, figw=None, figh=None):
    from PIL import Image as PILImage
    iw, ih = PILImage.open(path).size
    w = CW if w_ratio is None else CW * w_ratio
    h = w * ih / iw
    return Image(path, width=w, height=h)

# ================= 封面 =================
story.append(Spacer(1, 16*mm))
story.append(Paragraph(u'iCAN 大学生创新创业大赛 · AI Coding 赛道（Web 应用）', S['CoverKicker']))
story.append(Spacer(1, 10*mm))
story.append(Paragraph(u'云 帆', S['CoverTitle']))
story.append(Spacer(1, 4*mm))
story.append(Paragraph(u'AI 学习领航引擎 · 参赛作品应用方案', S['CoverSub']))
story.append(Spacer(1, 5*mm))
story.append(Paragraph(u'长风破浪 · 云帆济海', S['CoverSlogan']))
story.append(Spacer(1, 12*mm))
story.append(HRFlowable(width='40%', thickness=1, color=C_LINE))
story.append(Spacer(1, 12*mm))
intro = (u'「云帆」是面向大学生期末、考研、考公复习的 AI 学习领航引擎，取意"长风破浪会有时，'
         u'直挂云帆济沧海"——"云"喻云端智能，"帆"承科学方法。核心理念：认知科学定骨架、'
         u'AI 做个性化——间隔重复、测试效应、交错练习、认知负荷理论、自我效能感等九项实证研究'
         u'构成不可妥协的排序规则；大模型驱动学情诊断、每日复盘与编排解释，每个安排可解释、可溯源。'
         u'系统依据考试期限、掌握度、喜好与个人精力节律，每日自动生成"首胜—攻坚—自测—交错—复习—收尾"'
         u'六块式课表，以连击打卡维持动机，陪伴学子长风破浪、行稳致远。')
ibox = Table([[Paragraph(intro, ParagraphStyle('IntroBox', parent=S['Body'], fontSize=10,
                                               leading=17, alignment=TA_JUSTIFY, spaceAfter=0))]],
             colWidths=[CW*0.86])
ibox.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), C_PAPER),
    ('BOX', (0, 0), (-1, -1), 0.8, C_LINE),
    ('TOPPADDING', (0, 0), (-1, -1), 12),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ('RIGHTPADDING', (0, 0), (-1, -1), 14),
]))
ibox.hAlign = 'CENTER'
story.append(Paragraph(u'作品简介（200 字内）', ParagraphStyle('IntroT', parent=S['CoverKicker'],
                                                             fontSize=10, textColor=C_PRI,
                                                             fontName='CJK-Bold', spaceAfter=6)))
story.append(ibox)
story.append(Spacer(1, 26*mm))
story.append(Paragraph(u'2026 年 10 月', S['CoverKicker']))
story.append(NextPageTemplate('Main'))
story.append(PageBreak())

# ================= 目录 =================
story.append(Paragraph(u'目 录', S['TOCTitle']))
story.append(HRFlowable(width='100%', thickness=1, color=C_LINE, spaceAfter=12))
toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle('TOC0', fontName='CJK-Bold', fontSize=11.5, leading=20,
                   textColor=C_INK, leftIndent=2, wordWrap='CJK'),
    ParagraphStyle('TOC1', fontName='CJK', fontSize=10, leading=17,
                   textColor=C_SOFT, leftIndent=18, wordWrap='CJK'),
]
toc.dotsMinLevel = 0
story.append(toc)
story.append(PageBreak())

# ================= 一、目标用户与需求分析 =================
H1(u'一、目标用户与需求分析')
H2(u'1.1 目标用户群体')
P(u'云帆面向处于结构化备考期的大学生与毕业生，按备考场景分为三类核心人群。三类人群的共同特征是：'
  u'多科目（或多模块）并行、周期内有明确的截止考试、需要每天做出"学什么、何时学、学多久"的决策。')
story.append(TBL([
    [u'用户群体', u'场景特征', u'典型诉求'],
    [u'考研备考生', u'周期 6–12 个月；政治、英语、数学、专业课并行；自学为主', u'长周期科学规划，对抗遗忘，稳定执行不弃考'],
    [u'考公备考生', u'行测、申论、公基多模块训练；题量大；冲刺期集中', u'模块交错训练与限时自测，行测速度提升'],
    [u'期末备考生', u'周期 2–4 周；科目多、时间紧；作息受课程约束', u'短期高效排期，快速覆盖全部科目'],
], [CW*0.16, CW*0.46, CW*0.38]))
P(u'人群规模上，2026 年全国硕士研究生招生考试报名 343 万人（教育部，2025 年 11 月公布）；'
  u'2026 年度中央机关及其直属机构考试录用公务员共有 371.8 万人通过资格审查，实际参加笔试 283.1 万人。'
  u'叠加每学期期末季的在校生群体（全国普通本专科在校生约 3700 万人），目标用户总量达千万级。')

H2(u'1.2 核心痛点')
P(u'<b>计划靠感觉。</b>手工课表普遍按"平均分配"排时间，不区分科目的紧迫度与掌握度，'
  u'结果是强科反复过曝、弱科持续欠账，临考才发现时间错配。')
P(u'<b>复习违背记忆规律。</b>集中重读、无自测、无间隔安排，遗忘曲线之下大量投入失效。'
  u'认知心理学研究已反复证明检索练习与间隔重复相对被动重读的显著优势，但把结论落成工具的产品稀缺。')
P(u'<b>动机难以为继。</b>长周期备考中挫败感累积、正反馈缺失。2026 年度国考 371.8 万人过审、'
  u'283.1 万人参考——约每四名过审考生中就有一人未走进考场，弃考背后是计划崩塌后的自我放弃。')
P(u'<b>AI 工具"黑箱化"。</b>现有 AI 课表产品直接让大模型生成计划：无科学依据支撑，'
  u'无法解释"为什么这样排"，输出随模型波动，学生难以建立信任，更谈不上长期坚持。')

H2(u'1.3 功能需求分析')
story.append(TBL([
    [u'编号', u'用户需求', u'对应功能', u'依据来源'],
    [u'R1', u'按考试倒计时与掌握度分配各科时间', u'排程引擎：紧迫度 × 薄弱度权重', u'痛点一'],
    [u'R2', u'每天拿到可直接执行的课表', u'六块式今日时表，一键生成', u'痛点一'],
    [u'R3', u'防止学过就忘', u'间隔复习（+1 / +3 / +7 天）', u'间隔重复研究'],
    [u'R4', u'检验真实掌握程度', u'每日闭卷检索自测', u'测试效应研究'],
    [u'R5', u'保持学习动力', u'首胜开场、连击打卡、悬念收尾', u'自我效能感 / 动机理论'],
    [u'R6', u'适配个人作息与精力节律', u'精力曲线（晨型 / 均衡 / 夜型）', u'认知负荷理论'],
    [u'R7', u'AI 答疑诊断，且要有依据', u'AI 教练三功能 + 科学规则硬约束', u'痛点四'],
    [u'R8', u'账号与数据安全', u'QQ 邮箱注册、SHA-256 加盐哈希、验证码登录', u'基础需求'],
], [CW*0.08, CW*0.30, CW*0.38, CW*0.24]))

# ================= 二、开发平台 =================
H1(u'二、开发平台：秒哒')
H2(u'2.1 平台介绍')
P(u'秒哒（miaoda.cn）是面向大众的无代码 AI 应用搭建平台，主打"一句话做应用"：'
  u'用自然语言描述需求即可生成网页、小程序等应用，配合可视化编辑调整界面与逻辑；'
  u'平台内置大模型能力接入、数据管理与素材生成，支持一键发布并获得可访问链接，'
  u'同时提供应用广场用于作品展示与分发，教育类模板生态成熟。对参赛作品而言，'
  u'秒哒既是开发环境，也是发布与传播渠道。')
H2(u'2.2 开发流程与选型理由')
P(u'作品采用"原型先行、平台落地"的两段式开发流程：第一阶段以单文件 Web 应用完成算法与交互的'
  u'高保真原型（GitHub Pages 托管演示），排程引擎以纯函数实现并用 156 项自动化回归测试保障正确性；'
  u'第二阶段在秒哒平台以原型为蓝本重建并发布参赛版本，登录体系与 AI 能力对接平台内置组件。'
  u'这一流程让算法验证与平台适配解耦，降低返工风险。')
story.append(TBL([
    [u'选型考量', u'秒哒的对应能力'],
    [u'AI 为核心能力', u'原生集成大模型组件，即配即用，契合赛题对 AI 核心地位的要求'],
    [u'开发效率', u'自然语言生成 + 可视化编辑，个人开发者无需自建后端与运维'],
    [u'发布分发', u'一键发布、链接直达，满足"在平台搭建并发布"的参赛要求'],
    [u'生态曝光', u'应用广场与教育类模板，便于作品展示与早期用户获取'],
], [CW*0.24, CW*0.76]))

# ================= 三、技术方案 =================
H1(u'三、技术方案')
H2(u'3.1 总体架构：双引擎设计')
P(u'云帆的核心设计是一句话：<b>科学定律定骨架，AI 做个性化。</b>'
  u'认知科学规则引擎决定"什么任务排在什么位置"——这部分是硬约束，不随模型输出波动；'
  u'大模型在骨架之内做诊断、解释与微调建议——这部分因人而异、随时演进。')
story.append(TBL([
    [u'层次', u'组件', u'职责'],
    [u'交互层', u'启动页 / 今日 / 排期 / 科目 / 习惯 / AI 教练 / 科学 七大视图', u'全部交互与可视化'],
    [u'智能层（AI 软引擎）', u'大模型，OpenAI 兼容接口（默认百度千帆）', u'学情诊断、每日复盘、编排解释与微调建议'],
    [u'规则层（科学硬引擎）', u'排程引擎 generateDay 与九条实证规则', u'时间分配、任务排序、复习调度，AI 不可覆盖'],
    [u'数据层', u'本地存储 + 账号体系', u'多账号隔离、SHA-256 加盐哈希、JSON 导出'],
], [CW*0.20, CW*0.40, CW*0.40]))
H2(u'3.2 排程算法')
P(u'<b>（1）科目权重。</b>每科的时间配比由"紧迫度 × 薄弱度"决定：紧迫度随考试日期临近而上升，'
  u'薄弱度由难度与掌握度之差度量。权重归一化后得到各科时间占比（合计 100%）。'
  u'英语掌握度高则占比回落，数学薄弱且临近则占比抬升——时间流向最需要它的地方。')
P(u'<b>（2）精力曲线对齐。</b>按晨型、均衡、夜型三种作息类型建立日内精力曲线（多谐波模型，'
  u'含午间低谷与傍晚次峰），攻坚块自动对齐曲线峰值，自测等轻量任务安排在低谷时段。')
P(u'<b>（3）六块式结构。</b>每日时表由六类任务块依序构成，每一块对应一条实证研究：')
story.append(TBL([
    [u'顺序', u'任务块', u'内容', u'科学依据'],
    [u'1', u'首胜开场', u'偏好度最高的科目', u'自我效能感（Bandura）：以擅长领域制造开局正反馈'],
    [u'2', u'峰值攻坚', u'紧迫 × 薄弱最高的科目，对齐精力峰值', u'认知负荷理论（Sweller）：高负荷任务匹配高认知资源时段'],
    [u'3', u'检索自测', u'昨日新学内容闭卷测试', u'测试效应（Roediger、Karpicke，2006）'],
    [u'4', u'交错练习', u'多科混合练习', u'交错练习效应（Rohrer、Taylor）'],
    [u'5', u'间隔复习', u'3 天、7 天前所学', u'间隔重复（Cepeda 等 2006 元分析）'],
    [u'6', u'悬念收尾', u'留一道未解题次日揭晓', u'蔡加尼克效应：未竟任务提升次日回访动机'],
], [CW*0.07, CW*0.13, CW*0.32, CW*0.48]))
story.append(KeepTogether([
    IMG(CH1),
    Paragraph(u'图 1 · 晨型作息示例：六块式时表与日内精力曲线（算法示意，非固定排布）', S['Caption']),
]))
P(u'<b>（4）单元化排程。</b>时表以 25 分钟番茄单元（可调 50 分钟深度模式）为最小粒度，'
  u'按用户设定的每日学时预算生成，午间自动安排休整块；夜型用户的攻坚块整体后移。', 'BodyTight')
H2(u'3.3 账号与数据体系')
P(u'注册采用 QQ 邮箱加密码：密码须不少于 6 字符且同时包含大小写字母与特殊符号，'
  u'输入框下方强弱条按满足条件逐条点亮；密码经 SHA-256 加盐哈希后仅存本机，明文不落盘。'
  u'登录支持三种方式：密码登录、验证码登录（6 位数字、5 分钟有效、60 秒重发冷却）与游客模式，'
  u'忘记密码在登录页原位重置。工程上不依赖服务端 session，采用令牌式本地会话；'
  u'同一浏览器内多账号数据相互隔离，支持 JSON 一键导出备份。', 'BodyTight')
H2(u'3.4 质量保障')
P(u'排程引擎、账号体系、密码策略、验证码流程与动效降级共 156 项自动化回归测试'
  u'（node test.js 一键运行，算法改动必跑）。无障碍方面尊重系统"减少动态效果"偏好，'
  u'全部动画自动降级为静态呈现；启动页 Canvas 特效使用预渲染精灵与流场复用控制开销，'
  u'进入系统后停止渲染，不占用后台资源。', 'BodyTight')

# ================= 四、作品功能说明 =================
H1(u'四、作品功能说明')
H2(u'4.1 功能总览')
story.append(TBL([
    [u'模块', u'功能'],
    [u'启动页', u'海面焦散光影（Canvas 程序化生成）、光尘粒子随光标汇聚、流星划过，进入系统后特效停止'],
    [u'登录注册', u'密码 / 验证码双方式登录、注册、忘记密码原位重置、游客模式'],
    [u'设置向导', u'三步入档：考试类型 → 科目档案 → 个人习惯；支持一键载入示例数据'],
    [u'今日', u'一键生成六块式时表、任务打卡、连击统计、格言卡'],
    [u'排期', u'时间轴视图、精力曲线叠加、各科时间配比一览'],
    [u'科目', u'科目增删改、颜色标记、考试倒计时'],
    [u'习惯', u'作息与节奏设置、账号管理、数据导出与清空'],
    [u'AI 教练', u'学情诊断、每日复盘、编排顾问'],
    [u'科学', u'九条实证研究卡片，含出处与系统应用说明'],
], [CW*0.16, CW*0.84]))
H2(u'4.2 设置向导：三步入档')
P(u'首次注册后进入向导。第一步选择考试类型（考研 / 期末考 / 考公 / 自定义），系统自动预填典型科目；'
  u'第二步逐科录入难度、掌握度、喜好度（1–5 分）与考试日期——这四个维度正是排程权重与'
  u'首胜开场策略的输入；第三步设定作息（起床 / 就寝 / 每日学时）、精力类型与番茄节奏。'
  u'向导也提供"一键载入示例数据"，让新用户 30 秒内看到完整效果。')
H2(u'4.3 今日时表与打卡')
P(u'生成的时表逐块列出时段、科目、任务与依据标签。点击任意任务块的标签，弹窗展示'
  u'"为何这样排"的科学原理与文献出处；完成打卡触发连击计数与激励文案——首胜块完成时'
  u'提示"带着这份手感，去啃硬骨头"。在示例数据下，英语（喜好度 5）开场、政治（紧迫 × 薄弱最高）'
  u'攻坚的排序与算法输出一致，用户可即时验证系统的取舍逻辑。')
H2(u'4.4 特色交互')
P(u'启动页将品牌叙事视觉化：对角线冷暖渐变海面上，程序化焦散光网缓缓流动，光尘粒子在光标'
  u'300px 范围内汇聚成环。排期视图将时间轴与精力曲线叠加，攻坚块以朱砂色高亮并标注"攻坚峰值"。'
  u'科学页的每条研究都写明"在系统中的应用"，与任务块标签一一对应，构成完整证据链。', 'BodyTight')

# ================= 五、AI 功能的核心作用 =================
H1(u'五、AI 功能的核心作用')
H2(u'5.1 设计理念：领航员而非独裁者')
P(u'云帆将 AI 定位为"领航员"：九条科学规则构成不可妥协的排序骨架，AI 在骨架之内做个性化解释、'
  u'诊断与微调。系统提示词把全部科学规则注入为大模型的硬约束——AI 不得改变这些规则，'
  u'只做因人而异的解释与建议。这一机制从源头限制了大模型幻觉对学习计划的干扰，'
  u'是作品与"黑箱 AI 课表"的本质区别，也是评审可现场验证的差异点。')
H2(u'5.2 三大 AI 功能')
story.append(TBL([
    [u'功能', u'输入', u'输出', u'价值'],
    [u'学情诊断', u'大白话描述复习现状', u'诊断结论 + 科目档案调整建议 + 行动指令', u'把模糊焦虑转化为可执行调整'],
    [u'每日复盘', u'睡前三言两语的今日感受', u'三行复盘 + 明日最重要的一件事', u'低成本维持元认知与动机'],
    [u'编排顾问', u'自动读取科目档案与今日时表', u'排序解释 + 优化点', u'让每个安排可解释、可信任'],
], [CW*0.13, CW*0.25, CW*0.34, CW*0.28]))
H2(u'5.3 提示词工程')
P(u'系统提示词的约束包括：注入九条科学规则为不可违反的前提；回复使用中文、直接给结论、不客套；'
  u'长度不超过 220 字；给出建议时必须注明所依据的科学原理。接口兼容任意 OpenAI 风格端点'
  u'（默认百度千帆），密钥仅存本机；秒哒参赛版本切换为平台内置 AI 组件，约束逻辑保持不变。')
H2(u'5.4 可解释链路')
P(u'从任务块标签到依据弹窗，再到科学页的文献出处，每一环都可追溯，用户与评审都能查证'
  u'"为什么这样排"的答案。可解释不是附加说明，而是产品的信任基础——学生只会坚持自己理解的计划。', 'BodyTight')

# ================= 六、使用说明 =================
H1(u'六、使用说明')
H2(u'6.1 首次使用流程')
story.append(TBL([
    [u'步骤', u'操作', u'说明'],
    [u'1', u'打开作品链接，点击"进入系统"', u'启动页呈现品牌动效，回车键亦可进入'],
    [u'2', u'选择登录方式', u'注册（QQ 邮箱 + 强密码）/ 密码登录 / 验证码登录 / 游客模式先体验'],
    [u'3', u'完成三步设置向导', u'或点击"一键载入示例数据"快速体验'],
    [u'4', u'进入「今日」页，点击"生成今日时表"', u'约 1 秒生成当日六块式课表'],
    [u'5', u'按时表执行学习任务', u'点击任务块标签可查看科学依据'],
    [u'6', u'完成任务即打卡', u'连击计数 +1，触发激励提示'],
    [u'7', u'睡前到「AI 教练」做每日复盘', u'输入今日感受，约 3–10 秒返回复盘与明日建议'],
], [CW*0.08, CW*0.36, CW*0.56]))
H2(u'6.2 每日使用节奏')
P(u'晨间一键生成时表，白天按块执行与打卡，晚间用 30 秒向 AI 教练输入感受完成复盘。'
  u'次日的检索自测内容自动取自昨日攻坚块，复习内容自动取自 3 天、7 天前的学习日志——'
  u'用户全程无需手工维护复习清单，这是引擎自动化的部分。')
H2(u'6.3 交互指南')
story.append(TBL([
    [u'位置', u'操作', u'效果'],
    [u'启动页', u'移动光标', u'300px 范围内光尘粒子汇聚成环，圈外照常流动'],
    [u'今日 · 任务块', u'点击依据标签', u'弹窗显示该块的科学原理与出处'],
    [u'今日 · 打卡', u'点击圆形按钮', u'记录完成、连击 +1、显示激励文案'],
    [u'侧栏底部', u'游客点击账号条', u'唤起登录 / 注册界面'],
    [u'排期页', u'查看时间轴', u'各科分布与精力曲线叠加，攻坚块高亮'],
    [u'习惯页', u'点击导出数据', u'下载 JSON 备份文件'],
    [u'AI 教练', u'填写输入后发送', u'约 3–10 秒返回结构化建议'],
], [CW*0.18, CW*0.26, CW*0.56]))
H2(u'6.4 常见问题')
P(u'调整科目或考试日期后重新生成时表即可，历史记录保留；忘记密码经登录页"忘记密码？"原位重置，'
  u'学习数据不受影响；全部数据仅存本机浏览器，可随时导出或清空。', 'BodyTight')

# ================= 七、应用前景与商业模式 =================
H1(u'七、应用前景与商业模式')
H2(u'7.1 市场空间')
P(u'2026 年考研报名 343 万人、国考 371.8 万人过审，期末备考覆盖数千万在校生；'
  u'同期报名人数的理性回归，意味着考生正从"拼时长"转向"拼方法"，科学备考工具的相对价值上升。'
  u'政策层面，《教育强国建设规划纲要（2024—2035 年）》与国家教育数字化战略为 AI 学习工具'
  u'提供了明确导向。')
story.append(KeepTogether([
    IMG(CH2, w_ratio=0.82),
    Paragraph(u'图 2 · 全国考研报名与国考过审人数（万人）。数据来源：教育部（2025-11-24）；'
              u'国家公务员局 / 中国政府网（2025-10）。', S['Caption']),
]))
H2(u'7.2 应用前景')
P(u'纵向深化：错题本实体化、+15 天长间隔复习、周维度复盘视图；横向扩展：从备考编排延伸至'
  u'职业考证（法考、注册会计师、教师资格）与日常自主学习；工程演进：接入云端账号后实现跨设备'
  u'同步，匿名化数据可为高校学业支持部门提供群体学习状态画像。')
H2(u'7.3 商业模式')
story.append(TBL([
    [u'模式', u'内容', u'说明'],
    [u'C 端免费 + 增值', u'排程、打卡、科学页免费；AI 三功能按次或包月订阅', u'免费层保渗透，AI 调用成本由订阅覆盖'],
    [u'B2B2C', u'高校学生处、图书馆、考研机构按席位采购', u'机构版支持学情看板与冠名'],
    [u'内容合作', u'与考研名师、培训机构共建科目策略包', u'知识分成模式'],
], [CW*0.18, CW*0.46, CW*0.36]))
P(u'差异化壁垒在于三件事的叠加：经同行评议的科学规则库、逐块可溯源的可解释性、'
  u'本地优先的隐私设计——最后一点在数据合规日益收紧的背景下，正从技术选择变成卖点。', 'BodyTight')

# ================= 八、结语与个人开发说明 =================
H1(u'八、结语与个人开发说明')
H2(u'8.1 个人独立开发说明')
P(u'本作品由一名学生独立完成，覆盖需求分析、科学文献调研、排程算法设计、前后端实现、'
  u'动效打磨、回归测试与参赛文档全流程。独立开发之所以可行，关键在于 AI Coding 工作流：'
  u'科学规则库与双引擎架构由本人研究文献后定义，工程实现借助 AI 编程工具（秒哒平台 + '
  u'TRAE）高效落地——算法逻辑、156 项回归测试用例均由本人设计并逐一验证，AI 负责代码生成'
  u'与调试加速，每一处技术决策仍由本人把关。这一过程本身即是"AI Coding 赛道"精神的最好'
  u'注脚：一名学生 + AI 工具，即可完成过去需要一个团队才能交付的完整产品。', 'BodyTight')
story.append(Spacer(1, 3*mm))
story.append(TBL([
    [u'模块', u'个人完成方式'],
    [u'科学规则库', u'研读九项认知科学文献，提炼为可执行的排序规则'],
    [u'排程引擎', u'独立设计双引擎架构与六块式编排算法'],
    [u'工程实现', u'AI 辅助编码，本人审核全部技术决策与代码'],
    [u'质量保障', u'编写 156 项回归测试用例，全量通过'],
    [u'界面与动效', u'独立完成品牌视觉、焦散海面与粒子系统'],
    [u'文档与部署', u'秒哒平台搭建、GitHub Pages 部署、参赛文档撰写'],
], [CW*0.18, CW*0.82]))
H2(u'8.2 结语')
P(u'市面上的学习工具大多在回答"怎么学得更久"，云帆回答的是"怎么学得对"：让九条经过验证的'
  u'认知科学规律接管排序，让大模型做它擅长的解释与陪伴，让学生每天拿到一份看得懂、信得过、'
  u'执行得下去的课表。长风破浪会有时——云帆愿做学海之上那张会思考的帆。')
story.append(Spacer(1, 8*mm))
story.append(Paragraph(u'数据与文献来源', S['SrcTitle']))
for s in [
    u'教育部：2026 年全国硕士研究生招生考试报名人数 343 万（2025 年 11 月 24 日）',
    u'国家公务员局 / 中国政府网：2026 年度国考 371.8 万人通过资格审查、283.1 万人参加笔试',
    u'Roediger, H. L., 与 Karpicke, J. D. (2006). Test-Enhanced Learning. Psychological Science.',
    u'Cepeda, N. J., 等 (2006). Distributed Practice in Verbal Recall Tasks: A Review and Quantitative Synthesis. Psychological Bulletin.',
    u'Sweller, J. Cognitive Load Theory；Bandura, A. Self-Efficacy；Deci, E. L., 与 Ryan, R. M. Self-Determination Theory；Rohrer, D., 与 Taylor, K. Interleaving Practice；Zeigarnik, B. (1927) On Finished and Unfinished Tasks；Amabile, T. The Progress Principle.',
]:
    story.append(Paragraph(u'· ' + s, S['Src']))

doc.multiBuild(story)
print('PDF generated:', PDF_PATH)

from pypdf import PdfReader
r = PdfReader(PDF_PATH)
print('Pages:', len(r.pages))
print('Size: %.2f MB' % (os.path.getsize(PDF_PATH)/1024.0/1024.0))
