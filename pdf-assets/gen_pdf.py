# -*- coding: utf-8 -*-
"""云帆 · 参赛作品应用方案 PDF 生成脚本

按大赛通知「应用方案」要求组织内容：
  目标用户群体与功能需求 / 开发平台（秒哒·DuMate）/ 技术方案 /
  作品功能说明 / AI 功能的核心作用 / 完整使用说明（操作流程·交互指南）/
  应用前景与商业模式。输出 PDF，页数 ≤ 20，体积 ≤ 50 MB。
"""
import os, sys, io
BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.dirname(BASE)
PDF_PATH = os.path.join(OUT_DIR, u'云帆-参赛作品应用方案.pdf')
CH1 = os.path.join(BASE, 'chart_energy.png')
CH2 = os.path.join(BASE, 'chart_market.png')
CH3 = os.path.join(BASE, 'chart_ai_context.png')

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

def chart_ai_context():
    days = ['D-6', 'D-5', 'D-4', 'D-3', 'D-2', 'D-1', '今日']
    rate = [50, 67, 33, 67, 50, 67, 50]
    mood = [3.0, 3.0, 2.0, 3.0, 2.0, 2.0, 2.3]
    fig, ax1 = plt.subplots(figsize=(9.2, 3.5))
    x = np.arange(len(days))
    bars = ax1.bar(x, rate, color='#2F6B5E', width=0.5, alpha=0.9)
    for b, v in zip(bars, rate):
        ax1.text(b.get_x() + b.get_width()/2, v + 2, '%d%%' % v, ha='center', fontsize=8.6, color='#2F6B5E')
    ax1.set_ylabel('任务块完成率（%）', fontsize=10, color='#2F6B5E')
    ax1.set_ylim(0, 100)
    ax1.set_xticks(x)
    ax1.set_xticklabels(days, fontsize=9.5)
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    ax1.set_axisbelow(True)
    ax2 = ax1.twinx()
    ax2.plot(x, mood, color='#C7391B', lw=2.0, marker='o', ms=4.5)
    ax2.set_ylabel('情绪自评（1–5）', fontsize=10, color='#C7391B')
    ax2.set_ylim(1, 5)
    for s in ['top']:
        ax1.spines[s].set_visible(False)
        ax2.spines[s].set_visible(False)
    ax1.tick_params(labelsize=9.5)
    ax2.tick_params(labelsize=9.5)
    ax1.text(0.01, 0.94, '柱：近 7 日完成率    线：情绪自评', transform=ax1.transAxes,
             fontsize=9, color='#6B655A')
    fig.savefig(CH3, dpi=150, bbox_inches='tight')
    plt.close(fig)

chart_energy()
chart_market()
chart_ai_context()

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
    'CoverSub': ParagraphStyle('CoverSub', fontName='CJK-Bold', fontSize=18, leading=25,
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
    canv.drawString(ML, 9.5*mm, u'云帆 · 认知科学 × 大模型双引擎的 AI 学习领航引擎 — 参赛作品应用方案')
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

def IMG(path, w_ratio=None):
    from PIL import Image as PILImage
    iw, ih = PILImage.open(path).size
    w = CW if w_ratio is None else CW * w_ratio
    h = w * ih / iw
    return Image(path, width=w, height=h)

# ================= 封面 =================
story.append(Spacer(1, 14*mm))
story.append(Paragraph(u'iCAN 大学生创新创业大赛 · AI Coding 赛道（Web 应用）', S['CoverKicker']))
story.append(Spacer(1, 9*mm))
story.append(Paragraph(u'云 帆', S['CoverTitle']))
story.append(Spacer(1, 3*mm))
story.append(Paragraph(u'认知科学 × 大模型双引擎的 AI 学习领航引擎', S['CoverSub']))
story.append(Spacer(1, 4*mm))
story.append(Paragraph(u'长风破浪 · 云帆济海', S['CoverSlogan']))
story.append(Spacer(1, 9*mm))
story.append(HRFlowable(width='40%', thickness=1, color=C_LINE))
story.append(Spacer(1, 9*mm))
intro = (u'学海无涯，云帆济海。云帆是面向考研、考公、期末与职业考证的 AI 学习领航引擎：'
         u'以 10 项认知科学实证研究为不可妥协的排序骨架（间隔重复、测试效应、交错练习、认知负荷……），'
         u'大模型依托你的近 7 日完成率与情绪曲线做诊断、复盘与编排解释。'
         u'配套暖心护航（情绪打卡、12355 转介）、考试节点管家与大字无障碍模式，核心功能永久免费'
         u'——让县城自习室里的学生，也用得起一对一水准的科学督学。')
ibox = Table([[Paragraph(intro, ParagraphStyle('IntroBox', parent=S['Body'], fontSize=10,
                                               leading=17, alignment=TA_JUSTIFY, spaceAfter=0))]],
             colWidths=[CW*0.88])
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
story.append(Spacer(1, 20*mm))
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
H1(u'一、目标用户群体与功能需求')
H2(u'1.1 目标用户群体')
P(u'云帆面向处于结构化备考期的学生与毕业生。他们的共同特征是：多科目（或多模块）并行、'
  u'周期内有明确的截止考试、需要每天为"学什么、何时学、学多久"做决策。按场景分为四类核心人群。')
story.append(TBL([
    [u'用户群体', u'场景特征', u'典型诉求'],
    [u'考研备考生', u'周期 6–12 个月；政治、英语、数学、专业课并行；自学为主', u'长周期科学规划，对抗遗忘，稳定执行不弃考'],
    [u'考公 / 考证人群', u'行测、申论、公基或教资、法考、软考、四六级等模块化备考', u'模块交错训练与限时自测，短期高效覆盖'],
    [u'期末备考生', u'周期 2–4 周；科目多、时间紧；作息受课程约束', u'短期排期，快速覆盖全部科目'],
    [u'县域 / 农村学生\n（重点民生对象）', u'请不起一对一督学，缺乏方法指导，普遍依赖自我摸索', u'免费、低配置可用、离线的科学编排'],
], [CW*0.20, CW*0.44, CW*0.36]))
P(u'人群规模上，2026 年全国硕士研究生招生考试报名 343 万人（教育部，2025 年 11 月公布）；'
  u'2026 年度中央机关及其直属机构考试录用公务员共有 371.8 万人通过资格审查，实际参加笔试 283.1 万人；'
  u'叠加每学期期末季的在校生群体（全国普通本专科在校生约 3700 万人），目标用户总量达千万级。')

H2(u'1.2 核心痛点')
P(u'<b>痛点一：计划靠感觉，时间错配。</b>手工课表普遍按"平均分配"排时间，不区分科目的紧迫度与掌握度，'
  u'结果是强科反复过曝、弱科持续欠账，临考才发现时间用错了地方。')
P(u'<b>痛点二：复习违背记忆规律。</b>集中重读、无自测、无间隔安排，遗忘曲线之下大量投入失效。'
  u'认知心理学已反复证明检索练习与间隔重复相对被动重读的显著优势，但把结论落成工具的产品稀缺。')
P(u'<b>痛点三：备考心理危机。</b>长周期备考中挫败感累积、正反馈缺失。2026 年度国考 371.8 万人过审、'
  u'283.1 万人参考——约每四名过审考生就有一人未走进考场。弃考的背后是计划崩塌后的自我放弃，'
  u'而市面工具几乎只催"更努力"，无人接住情绪。')
P(u'<b>痛点四：教育资源不均。</b>县城与农村学生请不起一对一督学，名师课动辄数千元；'
  u'而"时间编排"这件事本质上可以由规则引擎完成——缺的是有人把它免费做出来。')
P(u'<b>痛点五：关键信息散落，错过即弃考。</b>报名开始/截止、网上确认、打印准考证等节点分散在'
  u'研招网、人事考试网等多个站点，错过一个节点就意味着全年备考白费，而现有学习工具无一提供节点提醒。')
P(u'<b>痛点六：AI 工具"黑箱化"。</b>现有 AI 课表产品直接让大模型生成计划：无科学依据支撑，'
  u'无法解释"为什么这样排"，输出随模型波动，学生难以建立信任，更谈不上长期坚持。')

H2(u'1.3 功能需求分析')
story.append(TBL([
    [u'编号', u'用户需求', u'对应功能', u'回应痛点'],
    [u'R1', u'按考试倒计时与掌握度分配各科时间', u'排程引擎：紧迫度 × 薄弱度权重', u'痛点一'],
    [u'R2', u'每天拿到可直接执行的课表', u'六块式今日时表，一键生成', u'痛点一'],
    [u'R3', u'防止学过就忘', u'间隔复习（+1 / +3 / +7 天）', u'痛点二'],
    [u'R4', u'检验真实掌握程度', u'每日闭卷检索自测', u'痛点二'],
    [u'R5', u'保持学习动力，低谷期被理解', u'首胜开场、连击打卡、悬念收尾 + 暖心护航', u'痛点三'],
    [u'R6', u'适配个人作息与精力节律', u'精力曲线（晨型 / 均衡 / 夜型）', u'痛点一'],
    [u'R7', u'平价甚至免费的科学督学', u'核心功能永久免费 + 单文件离线可用', u'痛点四'],
    [u'R8', u'不会错过报名 / 确认 / 准考证节点', u'考试节点管家：录入 + 倒计时提醒', u'痛点五'],
    [u'R9', u'情绪可以被看见、被接住', u'每日情绪打卡 + 危机词转介 12355 / 12356', u'痛点三'],
    [u'R10', u'AI 答疑诊断，且要有依据', u'AI 教练三功能 + 科学规则硬约束 + 数据参照系', u'痛点六'],
    [u'R11', u'视障 / 大龄学习者同样可用', u'大字模式、aria-label、键盘焦点环、读屏播报', u'痛点四'],
    [u'R12', u'账号与数据安全', u'全栈账号体系（bcrypt + JWT）与本地数据导出', u'基础需求'],
], [CW*0.08, CW*0.30, CW*0.40, CW*0.22]))

# ================= 二、开发平台 =================
H1(u'二、开发平台与技术路线')
H2(u'2.1 开发平台：秒哒 + DuMate')
P(u'参赛版本基于<b>秒哒（miaoda）</b>无代码 AI 应用搭建平台完成建立与发布，可运行链接为 '
  u'<b>https://app-eyuq3wersow1.miaoda.online</b>。秒哒主打"一句话做应用"：用自然语言描述需求即可生成'
  u'网页应用，配合可视化编辑调整界面与逻辑；平台内置大模型能力接入、数据管理与素材生成，'
  u'支持一键发布并获得可访问链接，同时提供应用广场用于作品展示与分发，教育类模板生态成熟。'
  u'对参赛作品而言，秒哒既是开发环境，也是发布与传播渠道。')
P(u'工程实现阶段使用 <b>DuMate</b> 作为 AI Coding 助手，承担代码生成、调试定位与文档撰写：'
  u'排程算法、双引擎架构、科学规则库由本人研究文献后定义，AI 负责把设计高效落成代码，'
  u'每一处技术决策仍由本人把关与验收。')
story.append(TBL([
    [u'选型考量', u'平台 / 工具的对应能力'],
    [u'AI 为核心能力', u'秒哒原生集成大模型组件，即配即用，契合赛题对 AI 核心地位的要求'],
    [u'开发效率', u'自然语言生成 + 可视化编辑，个人开发者无需自建后端与运维'],
    [u'发布分发', u'一键发布、链接直达，满足"在平台搭建并发布"的参赛要求'],
    [u'工程加速', u'DuMate 承担代码生成与调试，使一人完成过去需团队交付的完整产品'],
    [u'可验证性', u'同时在 GitHub Pages 部署零后端演示版，评审可任意环境直接打开核验'],
], [CW*0.22, CW*0.78]))

H2(u'2.2 开发流程：原型先行、三形态落地')
P(u'作品采用"原型先行、多形态落地"的开发流程：第一阶段以<b>单文件 Web 应用</b>完成算法与交互的'
  u'高保真原型（已部署至 GitHub Pages，零后端即可完整演示）；第二阶段在秒哒平台以原型为蓝本'
  u'重建并发布参赛版本，登录与 AI 能力对接平台内置组件；同时仓库内提供 <b>Next.js 全栈版</b>'
  u'（含 SQLite 数据层与 REST API），支持自建服务器 / Docker 私有化部署。'
  u'三形态共用同一套算法与交互规范，算法验证与平台适配解耦，显著降低返工风险。')
story.append(TBL([
    [u'形态', u'技术实现', u'适用场景'],
    [u'单文件前端（原型 / 演示）', u'原生 HTML + CSS + Vanilla JS，单文件 150 KB，无构建依赖', u'GitHub Pages 在线演示、离线使用、评委零门槛体验'],
    [u'秒哒参赛版（发布）', u'秒哒平台搭建，内置 AI 组件与账号体系', u'参赛评审、应用广场分发'],
    [u'Next.js 全栈版（私有化）', u'Next.js 14 + TypeScript + SQLite + JWT，Docker 一键部署', u'高校 / 机构私有化部署、跨设备云同步'],
], [CW*0.24, CW*0.44, CW*0.32]))

# ================= 三、技术方案 =================
H1(u'三、技术方案')
H2(u'3.1 总体架构：双引擎设计')
P(u'云帆的核心设计可以浓缩为一句话：<b>科学定律定骨架，AI 做个性化。</b>'
  u'认知科学规则引擎决定"什么任务排在什么位置"——这部分是硬约束，不随模型输出波动；'
  u'大模型在骨架之内做诊断、解释与微调建议——这部分因人而异、随时演进。'
  u'这一分工从架构上限制了模型幻觉对学习计划的影响。')
story.append(TBL([
    [u'层次', u'组件', u'职责'],
    [u'交互层', u'启动页 / 今日 / 排期 / 科目 / 习惯 / 暖心 / AI 教练 / 科学 八大视图', u'全部交互与可视化'],
    [u'智能层（AI 软引擎）', u'大模型，OpenAI 兼容接口（默认百度千帆）；秒哒版用平台内置 AI 组件', u'学情诊断、每日复盘、编排解释与微调建议'],
    [u'规则层（科学硬引擎）', u'排程引擎 generateDay 与十条实证规则', u'时间分配、任务排序、复习调度，AI 不可覆盖'],
    [u'数据层', u'本地存储（前端）/ SQLite（全栈）/ 平台数据（秒哒），多形态可迁移', u'多账号隔离、密码加盐哈希、JSON 导出备份'],
], [CW*0.20, CW*0.44, CW*0.36]))

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

H2(u'3.3 AI 的数据参照系')
P(u'AI 分析的质量取决于它"看见"多少数据。云帆每次调用都会自动组装一份<b>四段式学情摘要</b>：'
  u'档案段（科目、距考天数、掌握 / 喜好 / 难度）、今日段（时表任务块序列）、'
  u'<b>执行段</b>（近 7 日完成率、峰值攻坚块完成次数、连续打卡天数）、'
  u'<b>状态段</b>（近 7 日情绪均分与记录天数）。执行段与状态段是关键——它们让 AI 有了参照系，'
  u'于是它能说出"你峰值攻坚块 5 次里只完成 2 次，建议把每日学时从 8 小时降到 6 小时先拉完成率"，'
  u'而不是泛泛的"要劳逸结合"。')
story.append(KeepTogether([
    IMG(CH3, w_ratio=0.90),
    Paragraph(u'图 3 · AI 的数据参照系示意：近 7 日完成率（柱）与情绪自评（线）随每次提问一并进入提示词', S['Caption']),
]))

H2(u'3.4 民生模块的技术实现')
P(u'<b>数据主权优先。</b>前端形态的全部数据（含情绪记录）仅存于本机 localStorage，按账号隔离，'
  u'可一键导出 JSON，不上传任何服务器；全栈形态虽提供云同步，但由用户主动开启，且数据库为'
  u'单文件 SQLite、随项目打包，可随时带走。情绪数据属于敏感个人信息，本地优先是刻意的设计选择。')
P(u'<b>危机转介。</b>心情记录文本在前端做关键词检索（7 类极端表述），命中即弹出心理援助卡片，'
  u'给出 12355（共青团青少年服务台）与 12356（全国心理援助热线），全程离线判定、不联网分析。')
P(u'<b>无障碍。</b>全局支持大字模式（界面放大 116%）、aria-label 语义标注、focus-visible 键盘焦点环'
  u'与 Toast 读屏播报；尊重系统"减少动态效果"偏好，全部动画自动降级为静态呈现。', 'BodyTight')

H2(u'3.5 全栈与部署')
P(u'仓库内的 Next.js 全栈版提供完整账号与云同步能力：bcrypt 哈希密码、jose 签发 JWT 并以'
  u'httpOnly Cookie 承载、12 组 REST 路由（auth / subjects / plans / completions / moods / nodes / '
  u'profile / ai / health）、SQLite 单文件数据层与自动建表迁移、Docker 多阶段构建（非 root 用户 + '
  u'健康检查）。前端与后端解耦：前端通过一个云适配客户端（api-client.js）识别运行环境，'
  u'在纯静态托管下自动进入单机模式，不做无谓的后端请求。')
story.append(TBL([
    [u'能力', u'实现方式'],
    [u'认证', u'bcryptjs 哈希 + jose 签发 JWT + httpOnly Cookie（SameSite=Lax）'],
    [u'数据', u'better-sqlite3 单文件数据库 + 启动时自动建表迁移 + 一键导入本地旧数据'],
    [u'部署', u'Dockerfile 多阶段构建 + 健康检查 + 环境变量注入 JWT_SECRET'],
    [u'前端同步', u'npm run sync 从仓库根目录自动同步前端文件，避免双份文件不一致'],
], [CW*0.18, CW*0.82]))

H2(u'3.6 质量保障')
P(u'排程引擎为纯函数实现，输入相同则输出可复现，便于回归验证；前端脚本在提交前统一做语法校验'
  u'与逻辑回归（在 Node 沙箱中注入构造学情数据，校验完成率 / 情绪统计与 AI 提示组装结果）。'
  u'文案与科学叙事遵循"不越界"原则：凡有文献支撑的排序原则均标注出处，凡系统自定的参数'
  u'（如各任务块的时长配比）均明确标注为启发式设定，不冒充科学结论。', 'BodyTight')

# ================= 四、作品功能说明 =================
H1(u'四、作品功能说明')
H2(u'4.1 功能总览')
story.append(TBL([
    [u'模块', u'功能'],
    [u'启动页', u'海面焦散光影（Canvas 程序化生成）、光尘粒子随光标汇聚、流星划过；附公益声明与游客入口'],
    [u'账号体系', u'本机账号（强密码 + 加盐哈希）+ 云端账号（全栈版）/ 秒哒版对接平台账号；支持游客模式'],
    [u'设置向导', u'三步入档：目标类型 → 科目档案 → 个人习惯；8 种目标模板一键载入'],
    [u'今日', u'一键生成六块式时表、任务打卡、连击统计、情绪快捷打卡、考试节点倒计时提醒'],
    [u'排期', u'时间轴视图、精力曲线叠加、各科时间配比、考试节点管家'],
    [u'科目', u'科目增删改、颜色标记、考试倒计时'],
    [u'习惯', u'作息与节奏设置、大字模式、账号管理、数据导出与清空'],
    [u'暖心', u'情绪打卡与周视图、低分关怀卡、4-7-8 呼吸练习、心理援助资源、自我关怀科学卡'],
    [u'AI 教练', u'学情诊断、每日复盘、编排顾问三功能；未配置模型时给出动态示例输出'],
    [u'科学', u'十条实证研究卡片，含出处与"在系统中的应用"说明'],
], [CW*0.16, CW*0.84]))

H2(u'4.2 目标模板库与设置向导')
P(u'首次进入后进入三步向导。第一步选择目标类型——已内置考研、期末考、考公、教师资格、法考、'
  u'软考、四六级七套预设（外加自定义），一键载入典型科目组合，把录入门槛降到最低；'
  u'第二步逐科录入难度、掌握度、喜好度（1–5 分）与考试日期——这四个维度正是排程权重与'
  u'首胜开场策略的输入；第三步设定作息（起床 / 就寝 / 每日学时）、精力类型与番茄节奏。'
  u'向导也提供"一键载入示例数据"，让新用户 30 秒内看到完整效果。')

H2(u'4.3 今日时表与打卡')
P(u'生成的时表逐块列出时段、科目、任务与依据标签。点击任意任务块，弹窗展示'
  u'"为何这样排"的科学原理与文献出处；完成打卡触发连击计数与激励文案——首胜块完成时'
  u'提示"带着这份手感，去啃硬骨头"。在示例数据下，英语（喜好度 5）开场、政治（紧迫 × 薄弱最高）'
  u'攻坚的排序与算法输出一致，用户可即时验证系统的取舍逻辑。')

H2(u'4.4 暖心护航：把情绪纳入学习系统')
P(u'备考的最大风险常常不是"学不会"，而是"撑不住"。暖心护航把心理状态作为一等公民接入系统：'
  u'今日页顶部五色圆点一键情绪打卡；《暖心》页提供近七日情绪柱状图、状态偏低时的关怀卡片'
  u'（"低谷期可以减量但不弃跑，今天哪怕只完成首胜开场也算赢"）、可跟随动画完成的 4-7-8 呼吸练习；'
  u'心情记录命中极端表述时，立即弹出心理援助卡片与 12355 / 12356 热线。连击中断时系统采用'
  u'自我关怀话术而非愧疚式提醒——依据 Neff 的自我关怀理论，善待自己是续航而非松懈。')

H2(u'4.5 考试节点管家')
P(u'"错过一个节点，全年备考白费。"排期页支持录入报名开始 / 截止、网上确认、打印准考证、考试日等'
  u'节点，到期前 7 天在今日页置顶显示倒计时，3 天内标红提示。这一功能对应真实的弃考成因，'
  u'也是本作品最直接的民生落点之一。')

H2(u'4.6 无障碍与教育公平')
P(u'习惯页提供大字模式开关，界面整体放大 116%；全局补充 aria-label、键盘焦点环与读屏播报，'
  u'视障与大龄学习者同样可用。启动页与今日页明示"云帆公益版 · 核心功能永久免费"，'
  u'并把"把一对一督学的时间编排能力，免费给到每一位县城自习室里的同学"写进产品叙事。', 'BodyTight')

# ================= 五、AI 功能的核心作用 =================
H1(u'五、AI 功能的核心作用')
H2(u'5.1 设计理念：领航员而非独裁者')
P(u'云帆将 AI 定位为"领航员"：十条科学规则构成不可妥协的排序骨架，AI 在骨架之内做个性化解释、'
  u'诊断与微调。系统提示词把全部科学规则注入为大模型的硬约束——AI 不得改变这些规则，'
  u'只做因人而异的解释与建议。这一机制是本作品与"黑箱 AI 课表"的本质区别，'
  u'也是评审可现场验证的差异点。')
H2(u'5.2 三大 AI 功能')
story.append(TBL([
    [u'功能', u'输入', u'输出', u'价值'],
    [u'学情诊断', u'大白话描述现状（自动附带近 7 日执行与情绪数据）', u'诊断结论 + 科目档案调整建议 + 行动指令', u'把模糊焦虑转化为可执行调整'],
    [u'每日复盘', u'睡前三言两语（自动附带今日计划与实际完成清单）', u'三行复盘 + 明日最重要的一件事', u'低成本维持元认知与动机'],
    [u'编排顾问', u'自动读取档案、今日时表与执行数据', u'排序解释 + 优化点', u'让每个安排可解释、可信任'],
], [CW*0.13, CW*0.28, CW*0.31, CW*0.28]))
H2(u'5.3 AI 的数据参照系：从复读机到分析师')
P(u'多数 AI 学习工具只能泛泛而谈，根因是提示词里没有"你实际做得怎么样"。云帆把执行数据与'
  u'情绪数据一并拼入提示词（见 3.3 节）。以每日复盘为例，模型收到的不再只是用户的几句口述，'
  u'而是自动生成的"今日计划序列 + 实际完成（逐块 ✓ / ✗）+ 完成率 + 未完成清单"，'
  u'再叠加用户补充。有了参照系，AI 才能指出模式——例如"峰值攻坚块连续三次安排在午后低谷后'
  u'未能完成，建议调整时段而非加大时长"。')
H2(u'5.4 提示词工程与可用性兜底')
P(u'系统提示词的约束包括：注入十条科学规则为不可违反的前提；回复使用中文、直接给结论、不客套；'
  u'长度不超过 220 字；给出建议时必须注明所依据的科学原理。接口兼容任意 OpenAI 风格端点'
  u'（默认百度千帆），密钥仅存本机；秒哒参赛版本切换为平台内置 AI 组件，约束逻辑保持不变。'
  u'<b>可用性兜底：</b>当用户尚未配置模型（含纯静态演示环境）时，系统不再弹出阻断式配置框，'
  u'而是直接渲染一份<b>按真实学情动态拼装的示例输出</b>（首句带入真实科目与距考天数，'
  u'并标注"示例输出"角标），保证任何评审在任何环境点开都能看到完整、真有数据的分析结果。')
H2(u'5.5 科学叙事的分寸：区分"原则"与"参数"')
P(u'作品刻意避免"科学包装"：任务块的<b>顺序与原则</b>均有同行评议研究支撑，会在界面中标注出处；'
  u'而各任务块的<b>时长配比</b>（如峰值攻坚权重 2.6、交错练习 2.0）与科目权重系数，'
  u'是本系统为把课表落到具体分钟而设定的<b>启发式参数</b>，并非上述论文的直接结论——'
  u'在"为什么这样安排"弹窗中已明确说明。引用研究支撑"怎么排"，但不把自定数值冒充成科学定律。', 'BodyTight')

# ================= 六、使用说明 =================
H1(u'六、使用说明')
H2(u'6.1 首次使用流程')
story.append(TBL([
    [u'步骤', u'操作', u'说明'],
    [u'1', u'打开可运行链接（秒哒）', u'启动页呈现品牌动效并显示公益声明'],
    [u'2', u'点击"进入系统"', u'已有账号则直接进入；也可点"先逛逛 · 游客模式"零门槛体验'],
    [u'3', u'注册 / 登录（可选）', u'注册后可跨设备同步；游客模式下数据仅存本机'],
    [u'4', u'完成三步设置向导', u'选择目标类型（8 选 1）→ 录科目 → 设作息；或点"一键载入示例数据"'],
    [u'5', u'进入「今日」页，点击"生成今日时表"', u'约 1 秒生成当日六块式课表'],
    [u'6', u'按时表执行学习任务', u'点击任务块可查看科学依据；完成即打卡，连击 +1'],
    [u'7', u'在「今日」页顶部点选情绪圆点', u'一键记录今日状态（可选填文字，仅存本机）'],
    [u'8', u'在「排期」页录入考试节点', u'7 天内节点将在今日页置顶倒计时提醒'],
    [u'9', u'睡前到「AI 教练」做每日复盘', u'输入今日感受，返回三行复盘与明日建议'],
    [u'10', u'（可选）到「习惯」页开启大字模式', u'界面放大、键盘可操作、读屏可播报'],
], [CW*0.08, CW*0.38, CW*0.54]))
H2(u'6.2 每日使用节奏')
P(u'晨间一键生成时表，白天按块执行与打卡，状态不佳时到《暖心》页做一次呼吸练习或拨打援助热线，'
  u'晚间用 30 秒向 AI 教练输入感受完成复盘。次日的检索自测内容自动取自昨日攻坚块，'
  u'复习内容自动取自 3 天、7 天前的学习日志——用户全程无需手工维护复习清单，'
  u'这是引擎自动化的部分。')
H2(u'6.3 交互指南')
story.append(TBL([
    [u'位置', u'操作', u'效果'],
    [u'启动页', u'移动光标', u'300px 范围内光尘粒子汇聚成环，圈外照常流动'],
    [u'今日 · 任务块', u'点击任务块', u'弹窗显示该块的科学原理与出处'],
    [u'今日 · 打卡', u'点击圆形按钮', u'记录完成、连击 +1、显示激励文案'],
    [u'今日 · 情绪', u'点击五色圆点', u'一键记录今日情绪，再次进入《暖心》页可写详情'],
    [u'今日 · 节点提醒', u'查看置顶 chip', u'7 天内考试节点倒计时，3 天内标红'],
    [u'暖心页 · 关怀卡', u'点击"呼吸放松"', u'跟随动画完成 4 轮 4-7-8 呼吸'],
    [u'排期页', u'查看时间轴 / 录入节点', u'各科分布与精力曲线叠加；节点到期自动提醒'],
    [u'习惯页', u'点击导出数据 / 大字模式', u'下载 JSON 备份；界面整体放大'],
    [u'AI 教练', u'填写输入后发送', u'约 3–10 秒返回结构化建议（未配置模型时返回示例输出）'],
], [CW*0.20, CW*0.24, CW*0.56]))
H2(u'6.4 常见问题')
P(u'<b>担心要自己申请 AI 密钥？</b>不需要——未配置模型时三大 AI 功能会直接返回带有真实学情数据的'
  u'示例输出，可完整演示；配置任意 OpenAI 兼容接口后自动切换为真实模型分析。'
  u'<b>调整科目或日期后要重排吗？</b>重新生成时表即可，历史记录保留。'
  u'<b>数据安全吗？</b>前端形态全部数据仅存本机浏览器，可随时导出或清空；云同步由用户主动开启。', 'BodyTight')

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
H2(u'7.2 民生价值与社会效益')
P(u'本作品的社会价值不止于"提分"。其一，<b>教育公平</b>：把原本需要付费购买的一对一督学'
  u'时间编排能力，以免费、离线、低配置可用的形式下沉到县域与农村；其二，<b>心理守卫</b>：'
  u'把情绪打卡、呼吸放松与专业援助入口做进学习工具，接住"弃考"背后的心理坍塌；'
  u'其三，<b>信息普惠</b>：考试节点管家把散落在多个政府站点的关键时间点收拢成一处提醒；'
  u'其四，<b>数字包容</b>：大字模式与无障碍适配让视障、大龄学习者不被排除在外。'
  u'这些能力与商业价值并不冲突——它们恰好构成了最扎实的早期用户基础与口碑来源。')
H2(u'7.3 应用前景')
P(u'纵向深化：错题本实体化、+15 天长间隔复习、周维度复盘视图；横向扩展：从考研 / 考公延伸至'
  u'职业考证（法考、注册会计师、教师资格）与日常自主学习；工程演进：接入云端账号后实现跨设备'
  u'同步，匿名化数据可为高校学业支持部门提供群体学习状态画像（含情绪风险的早期识别）。')
H2(u'7.4 商业模式')
story.append(TBL([
    [u'模式', u'内容', u'说明'],
    [u'C 端免费 + 增值', u'排程、打卡、暖心护航、节点管家、科学页永久免费；AI 三功能按次或包月订阅', u'免费层保渗透与公平叙事，AI 调用成本由订阅覆盖'],
    [u'B2B2C', u'高校学生处、图书馆、考研机构按席位采购', u'机构版可提供学情看板与情绪风险预警'],
    [u'公益合作', u'乡村中学、公共图书馆自习室、高校学业帮扶项目', u'免费授权 + 联合署名，扩大社会影响'],
    [u'内容合作', u'与考研名师、培训机构共建科目策略包', u'知识分成模式'],
], [CW*0.18, CW*0.50, CW*0.32]))
P(u'差异化壁垒在于三件事的叠加：经同行评议的科学规则库、逐块可溯源的可解释性、'
  u'本地优先的隐私设计——最后一点在数据合规日益收紧的背景下，正从技术选择变成卖点。', 'BodyTight')

# ================= 八、结语与个人开发说明 =================
H1(u'八、结语与个人开发说明')
H2(u'8.1 个人独立开发说明')
P(u'本作品由一名学生独立完成，覆盖需求分析、科学文献调研、排程算法设计、前后端实现、'
  u'动效打磨、质量验证与参赛文档全流程。独立开发之所以可行，关键在于 AI Coding 工作流：'
  u'科学规则库与双引擎架构由本人研究文献后定义，工程实现借助秒哒平台与 DuMate 等 AI 工具'
  u'高效落地——算法逻辑、数据口径、验证用例均由本人设计并逐一核对，AI 负责代码生成与调试加速，'
  u'每一处技术决策仍由本人把关。这一过程本身即是"AI Coding 赛道"精神的最好注脚：'
  u'一名学生 + AI 工具，即可完成过去需要一个团队才能交付的完整产品。', 'BodyTight')
story.append(Spacer(1, 3*mm))
story.append(TBL([
    [u'模块', u'个人完成方式'],
    [u'科学规则库', u'研读十项认知科学文献，提炼为可执行的排序规则'],
    [u'排程引擎', u'独立设计双引擎架构与六块式编排算法'],
    [u'民生模块', u'独立设计暖心护航、节点管家、无障碍与隐私方案'],
    [u'工程实现', u'AI 辅助编码（秒哒 + DuMate），本人审核全部技术决策与代码'],
    [u'质量验证', u'纯函数引擎 + 语法校验 + 沙箱逻辑回归，算法改动必验'],
    [u'界面与动效', u'独立完成品牌视觉、焦散海面与粒子系统'],
    [u'文档与部署', u'秒哒平台搭建与发布、GitHub Pages 部署、参赛文档撰写'],
], [CW*0.18, CW*0.82]))
H2(u'8.2 结语')
P(u'市面上的学习工具大多在回答"怎么学得更久"，云帆回答的是"怎么学得对"：让十条经过验证的'
  u'认知科学规律接管排序，让大模型做它擅长的解释与陪伴，让学生每天拿到一份看得懂、信得过、'
  u'执行得下去的课表；再往前一步，让这份课表与它所照料的心情，免费地抵达最需要它的人。'
  u'长风破浪会有时——云帆愿做学海之上那张会思考的帆。')
story.append(Spacer(1, 8*mm))
story.append(Paragraph(u'数据与文献来源', S['SrcTitle']))
for s in [
    u'教育部：2026 年全国硕士研究生招生考试报名人数 343 万（2025 年 11 月 24 日）',
    u'国家公务员局 / 中国政府网：2026 年度国考 371.8 万人通过资格审查、283.1 万人参加笔试',
    u'Roediger, H. L., 与 Karpicke, J. D. (2006). Test-Enhanced Learning. Psychological Science.',
    u'Cepeda, N. J., 等 (2006). Distributed Practice in Verbal Recall Tasks: A Review and Quantitative Synthesis. Psychological Bulletin.',
    u'Hagger, M. 等 (2016). A multilab preregistered replication of the ego-depletion effect.',
    u'Neff, K. (2003). Self-compassion: An alternative conceptualization of a healthy attitude toward oneself.',
    u'Sweller, J. Cognitive Load Theory；Bandura, A. Self-Efficacy；Deci, E. L., 与 Ryan, R. M. Self-Determination Theory；Rohrer, D., 与 Taylor, K. Interleaving Practice；Zeigarnik, B. (1927) On Finished and Unfinished Tasks；Amabile, T. The Progress Principle.',
]:
    story.append(Paragraph(u'· ' + s, S['Src']))

doc.multiBuild(story)
print('PDF generated:', PDF_PATH)

from pypdf import PdfReader
r = PdfReader(PDF_PATH)
print('Pages:', len(r.pages))
print('Size: %.2f MB' % (os.path.getsize(PDF_PATH)/1024.0/1024.0))
