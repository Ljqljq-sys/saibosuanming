#!/usr/bin/env python3
"""AI算命大师 —— FateStar紫微斗数 + 模板解读引擎 | 零配置，零认证"""

import os
import sys
import socket
import threading
import webbrowser
import random
import hashlib
from datetime import datetime

import requests
from flask import Flask, request, jsonify

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

app = Flask(__name__)

FATESTAR_URL = "https://www.fatestar.top/api/ziwei"


def fetch_astrology(birthday):
    try:
        dt = datetime.strptime(birthday, "%Y-%m-%d")
        resp = requests.get(
            FATESTAR_URL,
            params={"year": dt.year, "month": dt.month, "day": dt.day,
                    "hour": 12, "gender": "male"},
            timeout=8,
            headers={"User-Agent": "FortuneApp/2.0"}
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        return data.get("data", data)
    except Exception:
        return None


# ============================================================
# 命理模板引擎
# ============================================================

STAR_PERSONALITY = {
    "紫微": ("帝王星坐命", ["天生自带主角光环，气场两米八！今日决策力MAX，适合主导方向性事务。","帝王之气加持，今天走到哪都是焦点，说话都带混响 👑","今天你就是人群中的紫微星，优柔寡断不存在的好吗","自信是最好的风水，今天做什么都有一种天然的领导力"], 4),
    "天机": ("智多星坐命", ["脑袋转得比CPU还快，今天适合头脑风暴、搞创意、做方案。","智商在线的一天，复杂问题到你手里迎刃而解 🧠","今天灵感像连了WiFi，各种idea自动下载中……","聪明灵活是你的超能力，今天特别适合解决难题"], 4),
    "太阳": ("太阳星坐命", ["走到哪亮到哪！今天适合主动出击，展现自己的热情和魅力。","正能量辐射全宇宙，今天你就是行走的小太阳 ☀️","热情是你最强的磁场，今天大胆发光就对了","今天适合当人群中的C位，自信放光芒"], 4),
    "武曲": ("武曲星坐命", ["刚毅果决，执行力爆表。今天适合处理积压任务、推进项目。","行动力拉满的一天，说干就干不磨叽 💪","财星坐命，今天对事情的判断特别果断靠谱","今天适合用执行力碾压一切拖延症"], 4),
    "天同": ("天同星坐命", ["福星高照，心态稳如老狗。今天适合享受生活，顺其自然。","佛系但不摆烂，今天用一种轻松的方式把事情做了 🧘","福气值满格，今天凡事都有小幸运加持","不争不抢反而收获最多，今天做自己就好"], 4),
    "廉贞": ("廉贞星坐命", ["执着又多变，今天创意灵感迸发，但也容易纠结小事。","创意井喷但注意力容易分散，记得抓重点 🎨","今天脑子里全是idea，选一个最好的去执行就好","感性理性反复横跳的一天，跟着直觉走不会错"], 3),
    "天府": ("天府星坐命", ["稳重包容，天生的管理者。今天适合统筹规划、当和事佬。","稳如磐石的一天，泰山崩于前而色不变 🏰","管理才能在线，今天适合做资源协调和团队统筹","包容力MAX，今天当个好听众比当个好说客更有收获"], 4),
    "太阴": ("太阴星坐命", ["温柔细腻，直觉敏锐。今天适合做需要细心和审美的事。","细腻的感知力今天特别强，适合做品质把关 🌙","第六感准得吓人，相信直觉做的判断八成对","温柔但有力量，今天用巧劲比用蛮力效果好"], 4),
    "贪狼": ("贪狼星坐命", ["多才多艺，魅力四射！今天桃花和机会都多，但要学会选择。","才艺展示的一天，你的隐藏技能今天都能派上用场 🎭","魅力和才华双在线，但选择太多也是个甜蜜的烦恼","今天社交运爆棚，但记得给自己留点独处时间"], 3),
    "巨门": ("巨门星坐命", ["口才一流，但也容易惹是非。今天说话前先过脑子，避免误会。","表达能力拉满，但话多容易失言，拿捏分寸很重要 🗣️","今天适合深度思辨和分析，但别把辩论变成抬杠","逻辑清晰但也要兼顾人情，同样的话换种说法更温柔"], 3),
    "天相": ("天相星坐命", ["天生的辅佐之才，今天适合团队协作、帮人解决问题。","助人为乐的一天，帮别人解决问题自己也有收获 🌸","团队里的润滑剂，今天适合当和事佬和协调者","温和的力量今天特别强大，润物细无声地影响周围"], 4),
    "天梁": ("天梁星坐命", ["老中医体质——稳重长寿，今天适合养生、照顾他人。","经验之谈今天特别值钱，你的建议会被认真对待 🦉","成熟稳重的气质拉满，今天适合做复盘和优化","长者风范的一天，照顾好自己的同时也温暖了别人"], 4),
    "七杀": ("七杀星坐命", ["敢冲敢拼的冒险家！今天适合挑战新领域，但别太莽撞。","勇气值爆表的一天，直面挑战就是最好的策略 ⚔️","今天适合单枪匹马闯难关，一个人就是一支军队","冲劲十足但记得刹车，勇气和鲁莽之间隔着一个深呼吸"], 3),
    "破军": ("破军星坐命", ["不破不立！今天可能有意外的变化，拥抱改变会有惊喜。","变革之星当值，旧的不去新的不来，拥抱变化 🌊","今天适合打破常规，按常理出牌不是你的风格","待在舒适区外面才是你的舒适区，冲就完了"], 3),
}

STAR_CAREER = {
    "紫微": ["今天是职场主角，大胆发言、主动承担，领导会注意到你 🚀","帝王星加持，今天做决策特别准，适合拍板定大方向 📋","自带威严光环，会议上发言特别有分量，把握机会 💼","今天适合带领团队冲锋，你的领导力在线上级看得见 👑"],
    "天机": ["脑子灵光，适合做策略规划、写方案、搞创意，idea一个接一个","今天智商在线，复杂问题到你手里都能拆解清楚 🧩","创意井喷的一天，把灵感记下来说不定就是下一个爆款 💡","适合做研究、分析数据、写代码，脑力劳动的效率特别高 🔬"],
    "太阳": ["主动发光发热，适合做汇报、主持、对外沟通，存在感拉满","今天你是全场的焦点，大胆展示自己别藏着掖着 ☀️","正能量爆棚，适合激励团队、做宣讲、带节奏 🌻","对外沟通运特别好，客户谈判、面试、演讲都顺风顺水 🎤"],
    "武曲": ["执行力MAX，适合一口气解决堆积任务，KPI收割机模式启动","今天适合处理财务、合同、数据类工作，一针见血 💪","行动力拉满，说干就干不拖延，把待办清单清空 📋","适合做需要毅力和专注力的事，攻坚项目、冲刺deadline ⚡"],
    "天同": ["不卷不焦虑，按自己的节奏来。做点自己喜欢的、有成就感的事","佛系工作法今天最有效，放松反而效率高 🧘","适合做创意类、轻松的任务，别给自己太大压力 🎨","今天适合当团队的润滑剂，调和气氛、帮人解围 🤝"],
    "廉贞": ["创意灵感爆棚，适合搞创作写代码，但注意别纠结细节到深夜","今天思维活跃但也容易分心，建议列清单逐个击破 📝","适合做需要想象力的工作，设计、写作、策划都顺手 ✍️","注意别在细节上纠结太久，完成比完美更重要 🎯"],
    "天府": ["稳扎稳打的一天，适合做规划、整理、统筹，当好团队的定海神针","今天适合做长远规划，眼光放远布局未来 📐","管理能力在线，适合处理复杂项目、协调资源 🏗️","稳重的气场让同事信赖，今天可能被请教问题或征求意见 🦉"],
    "太阴": ["细心+审美在线，适合做设计、排版、润色类工作，质量优先","今天第六感特别准，相信直觉做判断不会错 🌙","适合做需要耐心和细致的工作，精雕细琢出精品 💎","温和的沟通方式今天特别有效，适合处理人际关系 🤗"],
    "贪狼": ["社交力MAX，今天适合拓展人脉、谈合作，但注意别画太多饼","今天适合对外联络、跑客户、参加活动，人脉即资源 🎭","多才多艺的一天，可以同时推进多个项目但注意优先级 🎪","魅力值在线，适合做需要说服力的工作，比如销售、演讲 🎤"],
    "巨门": ["口才在线但容易说多错多，今天少说多做，把精力放在实操上","今天适合做分析、研究、深度思考类工作，话少质量高 🔍","适合处理需要逻辑和批判性思维的任务，找bug一把好手 🐛","注意沟通方式，同样的话换种说法效果天差地别 🗣️"],
    "天相": ["辅助能力拉满，今天适合帮同事、做支持性工作，好人缘+1","今天适合做协调、对接类工作，各方资源你都能盘活 🔗","团队协作运最好，适合开脑暴会、结对工作 👥","服务意识在线，帮别人解决问题自己也会收获成就感 🌟"],
    "天梁": ["适合做复盘、优化、查缺补漏，你的经验和稳重今天很值钱","今天适合做质量把控、审核、校对类工作，火眼金睛 👀","经验就是财富，今天你踩过的坑都能帮别人避开 🧓","适合做教育、咨询、指导类工作，助人者天助 🏥"],
    "七杀": ["冲劲十足！适合攻坚克难、啃硬骨头，但注意别跟同事硬刚","今天适合做有挑战性的任务，越难越兴奋，迎难而上 ⚔️","适合独立作战，一个人顶一个团队，专注力爆表 🎯","注意控制脾气，冲劲是好事但别变成冲动 💥"],
    "破军": ["变革的一天，可能有突发任务或方向调整，适应就好，说不定是新机会","今天适合打破常规、尝试新方法，不拘一格降灵感 🌪️","适合做创新、改革类工作，旧的模式该推翻了 🔄","计划赶不上变化，但变化中藏着机会，保持灵活 🌊"],
}

STAR_WEALTH = {
    "紫微": ["💰 财运稳中有升，适合做长线规划，别冲动消费就OK","💎 正财稳定，适合做储蓄计划和资产配置 📊","👑 今天的消费建议：买需要的不是想要的，品质优先","🏦 适合研究长期理财，定投、保险类产品值得关注"],
    "天机": ["🧠 偏财运不错！可能是信息差、一个小idea带来的收入机会","💡 知识变现的一天，你的专业技能可能带来额外收入","🔍 适合研究新兴投资领域，但先学习再下手","📱 留意身边的信息差机会，可能是一个小副业的开始"],
    "太阳": ["📊 正财运在线，做好本职工作就有回报，不求暴富但求稳定","☀️ 光明正大赚钱，今天适合谈加薪、谈项目报酬","🌟 你的努力被看见了，可能有奖金或表扬伴随收入提升","🎯 稳扎稳打地赚钱，今天的收入对得起你的付出"],
    "武曲": ["💪 武曲是财星！今天适合研究理财产品、谈薪资、签合同","💰 今天对钱特别敏感，理财决策比较靠谱","📈 适合做大额支出的规划研究，比如买房买车的大方向","🏆 努力工作就有回报的一天，付出和收获成正比"],
    "天同": ["🎨 财运平稳，知足常乐。小确幸型的消费——一杯奶茶的快乐","😊 今天财运不求大富大贵，小钱进账不断就很好","🍀 适合犒劳自己一下，花点小钱买开心","🎁 可能收到小礼物或被请吃饭，财运小小的暖"],
    "廉贞": ["🔥 财运波动，可能有意外支出但也有意外收入，注意记账","💸 今天管住手！冲动消费的诱惑特别大","🎰 偏财运起伏大，不做赌博性质的投入","📝 建议记账，今天花钱的地方可能比较零散"],
    "天府": ["🏠 稳健型理财，今天适合做预算、存钱、研究房产类资产","🏛 长期投资眼光在线，适合做资产配置规划","📋 今天适合整理账单、清理订阅、优化开支结构","🔐 保守理财的一天，不亏就是赚"],
    "太阴": ["🌙 细水长流型财运，小额进账不断，适合做副业小尝试","💎 隐形收入可能比明面上的多，留意被忽略的资产","🌸 今天的财运藏在细节里，认真对账可能有惊喜","🛍 适合买性价比高的东西，省钱也是赚钱的一种"],
    "贪狼": ["🎭 桃花财！社交场合可能带来赚钱机会，但也要小心冲动消费","🍷 社交开销大但也可能带来机会，把握好度","🎪 人脉即钱脉，今天请客吃饭可能是投资","💃 娱乐和消费要平衡，开心就好但别超预算"],
    "巨门": ["🤔 财运一般，今天不适合投资决策，先观察再行动","🔍 适合研究但不适合下手，多做功课少掏钱","🧮 今天对数字敏感，适合做财务分析和预算","🤫 低调处理金钱事务，财不露白"],
    "天相": ["🤝 合作生财，今天适合谈合作、对接资源，借力打力","👥 团队项目可能带来分红或奖金，合作共赢","🔗 牵线搭桥也可能带来财运，帮别人介绍资源有回报","🌟 服务他人带来的回报可能比预期的多"],
    "天梁": ["🏛 财运稳定偏保守，今天适合储蓄和规划，别碰高风险投资","👴 经验变现的一天，你的专业知识值钱","💊 适合关注保险、养老金等长期保障型产品","📚 投资自己是最好的理财，花钱学习不亏"],
    "七杀": ["⚔ 大刀阔斧的一天，可能有大的收支变动，决策前三思","🔥 冲动消费的念头特别强，买大件之前先冷静24小时","💥 可能有意外收入但也可能有突发开支，预留缓冲","🎯 专注一个财务目标，分散反而容易出问题"],
    "破军": ["🌊 财运起伏大，可能有意外开支，但也可能有意外的进账","🎲 今天财务上可能有新变化，保持开放心态迎接","🔄 旧的收入模式可能改变，新的机会正在酝酿","⚡ 快进快出的财运，不适合长期锁定资金"],
}

STAR_LOVE = {
    "紫微": ["💜 气场强大吸引目光，今天容易被人暗恋或搭讪，保持微笑就好","👑 自信的样子最有魅力，今天适合主动出击 🎯","✨ 今天的你在人群中特别闪耀，桃花自动上门","💜 遇到心动的人别犹豫，帝王星的直觉不会错"],
    "天机": ["💡 聪明的大脑就是最好的魅力，今天的深度聊天会让人心动","🧠 机智幽默的一天，用才华吸引人比颜值更持久","💬 今天聊天的节奏特别好，能说到对方心坎里","📚 在图书馆、书店、课程中可能邂逅有趣的灵魂"],
    "太阳": ["☀ 热情主动就是你的必杀技，今天适合主动约人、表达好感","🌻 阳光般的笑容今天杀伤力翻倍，多笑笑桃花自然来","🎤 今天适合表白或发出约会邀请，成功率较高","🏃 运动场合、户外活动是邂逅的好场景"],
    "武曲": ["💎 低调务实反而吸引人，认真工作的样子最有魅力","💪 靠谱的气质今天特别加分，有人就喜欢踏实型的","🏋️ 健身、运动时的你最有魅力，自律的人闪闪发光","🤝 通过工作或共同目标认识的人值得留意"],
    "天同": ["🌈 轻松自在的状态最迷人，适合跟喜欢的人一起放松","🧘 不刻意的相处最舒服，今天的桃花是自然而然的那种","🎮 一起玩游戏、看电影、吃好吃的，简单约会最甜","🍵 佛系等桃花反而更容易来，放轻松就好"],
    "廉贞": ["🔥 魅力值在线但容易纠结，遇到对眼的人可以大胆一点","💋 神秘感今天特别吸引人，欲言又止的样子让人好奇","🎨 艺术气质拉满，展览、演出、livehouse是桃花高发区","💭 别想太多，今天跟着感觉走反而不会错"],
    "天府": ["🏰 稳重可靠的气质，容易让人觉得有安全感，桃花质量不错","🤗 包容大气的样子特别加分，今天可能被依赖型的人吸引","🏠 居家型的魅力今天爆表，做饭收拾房间都显得很迷人","👨‍👩‍👧 家庭聚会、朋友介绍是桃花来源，别拒绝相亲"],
    "太阴": ["🌙 温柔体贴最动人，今天的小细节会让对方印象深刻","💐 细腻的心思今天特别容易被感知，暗恋可能变明恋","🌸 温柔但不软弱，外柔内刚的气质是致命吸引力","🕯️ 浪漫的场合——咖啡厅、书店、公园——桃花潜伏中"],
    "贪狼": ["🎭 桃花朵朵开！但要注意分辨正桃花和烂桃花，别来者不拒","💃 社交场合的明星，今天可能同时被多个人示好","🍷 约会、party、聚会中的你魅力四射，但别喝多了上头","🎪 桃花质量参差不齐，用心感受比用眼睛看靠谱"],
    "巨门": ["🗣 今天表达能力拉满，聊得来就是缘分，但注意别怼人","💬 深度交流可能擦出火花，灵魂共鸣比表面吸引动人","🤔 今天容易被有思想深度的人吸引，智性恋的一天","📢 注意说话语气，温柔版的你桃花运会好很多"],
    "天相": ["🌸 温和体贴的魅力，今天适合当个贴心的倾听者","🤝 好人缘带来好桃花，朋友的朋友值得留意","💝 今天适合为喜欢的人做点小事，暖心比浪漫管用","🫶 配合度很高的一天，约会就听对方的也挺好"],
    "天梁": ["🦉 成熟稳重的气质吸引人，可能收到长辈介绍的对象","👴 今天可能被比自己成熟的人吸引，大叔/御姐型桃花","💊 照顾好自己也会吸引桃花，健康的生活方式很有魅力","📖 人生阅历带来的深度是今天的加分项"],
    "七杀": ["⚡ 直来直去的魅力，喜欢就大胆追，但不喜欢的也直接拒绝","🔥 敢爱敢恨的一天，主动出击比被动等待效果好","🎯 目标明确不拖泥带水，这种痛快劲反而吸引人","💥 一见钟情的概率较高，但别太快下结论"],
    "破军": ["🌪 桃花来的快去得也快，今天的心动可能是一见钟情式的","🎢 感情上可能有意外惊喜，比如突然收到表白","🔄 前任可能突然出现，要不要回头自己冷静决定","⚡ 心动的感觉很强烈，但先观察一下再说"],
}

GENERAL_CAREER = [
    "今天适合按自己的节奏来，不卷也不躺，做好手头的事就很好 🎯",
    "事业运平稳上升，保持专注，机会在不起眼的地方 🍀",
    "今天学新东西特别快，适合充电和技能提升 📚",
    "工作中可能遇到小挑战，但你能轻松应对 💪",
    "团队协作运不错，多跟同事交流会有意外收获 🤝",
    "今天适合整理工作流，优化效率比蛮干重要 🔧",
    "有贵人运！可能是领导或前辈的一句指点 🌟",
    "不要急着做决定，今天的观察比行动更重要 👀",
    "创造力和执行力都在线，是效率很高的一天 ⚡",
    "把大任务拆成小步骤，一件件来会很有成就感 ✅",
    "今天适合处理拖延已久的事情，做完会特别爽 🔥",
    "沟通运不错，适合做汇报、写邮件、对接需求 📧",
]

GENERAL_WEALTH = [
    "💰 财运平稳，不奢求暴富但求安心，小钱也是钱",
    "💵 今天的消费建议：买需要的而不是想要的",
    "🪙 财运小吉，可能有意外小红包或退款到账",
    "💳 控制购物欲的一天，先把购物车放一放",
    "📊 正财稳定，做好分内事就有回报",
    "🎁 可能有小惊喜——被请客、打折捡漏之类",
    "💡 今天适合研究理财知识，但先别急着下手",
    "🏦 存钱也是赚钱，今天适合做储蓄计划",
    "🛒 货比三家不吃亏，今天适合比价再下单",
    "💎 财运藏在细节里，认真记账会发现漏掉的收入",
    "📈 投资自己是最好的理财，花钱学技能不亏",
    "🔐 保守一点好，今天不适合高风险操作",
]

GENERAL_LOVE = [
    "💕 桃花运势平稳，随缘就好，不强求反而有惊喜",
    "💗 今天适合提升自己，自信的人最有魅力",
    "💌 可能会收到一条让你心动的消息",
    "🌸 温柔对待身边的人，好感度在悄悄上升",
    "🫶 今天适合跟喜欢的人分享日常，平淡最甜",
    "💝 单身的话先享受单身，有伴的话适合腻在一起",
    "🎀 小确幸型桃花，可能发生在咖啡店或地铁站",
    "💘 友情以上恋人未满？今天可能有小进展",
    "💓 心动不如行动，但别太急，先试探一下",
    "🌷 今天的你有一种不经意的魅力，做自己就好",
    "🦋 暧昧让人受尽委屈，但今天的暧昧是甜的",
    "💞 有伴的人今天适合一起做一件新鲜事",
]

YUNSHI_MODS = {
    "开心": ["运势翻倍！", "好运buff叠加中！", "锦鲤附体！"],
    "积极": ["冲劲满满！", "能量值拉满！", "干劲十足！"],
    "平静": ["稳如泰山。", "岁月静好。", "波澜不惊。"],
    "低落": ["触底反弹中…", "乌云会散的。", "蹲得越低跳得越高。"],
    "焦虑": ["深呼吸，运势不差。", "别急，好事在后头。", "稳住就能赢。"],
    "烦躁": ["水逆退散中…", "霉运退退退！", "冷静下来再看。"],
}

DO_ACTIONS = [
    "主动出击搞副业", "专注搞定学习任务", "约人聊合作", "花时间学新技能",
    "投资自己——读书充电", "发朋友圈秀成果", "做一顿美食犒劳自己", "整理一下房间",
    "尝试新运动", "给自己安排一个放松日", "联系老朋友聊聊", "开始计划旅行",
    "认真思考职业方向", "订个小目标：早起", "主动帮别人解决问题", "大胆说出你的想法",
    "推一个积压的PR", "去运动顺便听播客", "整理一下财务账单", "花30分钟搞定一个bug",
    "写日记记录心情", "学做一道新菜", "整理电脑桌面", "约朋友喝咖啡", "买一本想看的书",
    "多喝水保持精力", "听一首喜欢的歌", "对镜子里的自己笑一下", "给爸妈打个电话",
    "午休20分钟充电", "列一份本周计划清单", "删掉不用的APP", "清理手机相册",
    "手写一封信给自己", "逛公园呼吸新鲜空气", "尝试冥想5分钟", "换一条新路线通勤",
    "跟同事分享零食", "整理衣柜断舍离", "学一个快捷键提升效率", "备份重要文件",
    "吃一顿营养早餐", "早睡15分钟", "读一篇深度好文", "帮陌生人一个小忙",
    "把自己的idea写下来", "做一次眼保健操", "收藏的好课开始看第一节", "换一张新壁纸",
    "把欠的电影看了", "拍一张今天的天空", "对服务人员说声谢谢", "晒晒太阳补充维D",
    "记录今天的三个小确幸", "把快递拆了别堆着", "泡一杯好茶慢慢品", "做10个俯卧撑",
    "回复一条拖延已久的消息", "整理浏览器书签", "给自己买一束花", "把旧衣服捐掉",
    "学一个外语单词", "用左手刷牙（激活右脑）", "做一次深度复盘", "饭后散步15分钟",
]

DONT_ACTIONS = [
    "冲动做重大决定", "熬夜刷手机到凌晨", "跟人争论无关紧要的事", "暴饮暴食垃圾食品",
    "在群里乱发消息刷屏", "冲动消费买买买", "跟同事内卷较劲", "一个人emo胡思乱想",
    "把重要的事拖到明天", "相信天上掉馅饼的鬼话", "在深夜做人生决策", "跟对象翻旧账",
    "轻信陌生人的投资建议", "被别人PUA你的选择", "跟风投资不做功课", "过度解读别人的话",
    "边开会边刷短视频", "在地铁上外放看剧", "把情绪发泄在亲近的人身上", "空腹喝三杯咖啡",
    "凌晨还在焦虑工作的事", "一次性答应所有人的请求", "不吃饭靠奶茶续命", "同时开10个网页看",
    "刷完朋友圈又刷微博又刷抖音", "穿没干透的衣服出门", "跟网友抬杠对线", "反复查看前任的社交动态",
    "把所有钱都投进一个理财产品", "随手下App不看清权限", "边充电边玩手机到发烫", "在工位上一坐就是半天不动",
    "口嗨答应做不到的事", "用明天再说的心态逃避", "等快过期了才开始处理正事", "把坏情绪带到第二天",
    "跟不太熟的人掏心掏肺", "在朋友圈发泄负能量", "因为不好意思拒绝就勉强答应",
    "边吃饭边刷剧结果吃多了", "大半夜看美食视频然后点外卖", "从来不备份觉得不会出事",
    "拿自己的短板跟别人的长板比", "把今天的事赖给昨天的自己", "因为打折买不需要的东西",
    "在公共场合大声接电话", "看到消息已读不回装死", "把没验证过的谣言转发到家族群",
    "长时间戴耳机音量开太大", "把水果放到烂了才想起来吃", "把袜子攒一周一起洗",
    "坐椅子上跷二郎腿一整天", "用牙咬开瓶盖", "把密码设成123456",
    "觉得自己不行就还没开始就放弃", "在背后议论同事的是非", "把锅甩给客观条件",
]

MOOD_BOOST = {
    "开心": ["心情好就是最好的风水，今天好运加倍！", "开心就是开运！继续保持这个状态！", "心情好运气自然好，今天干啥都顺！"],
    "积极": ["积极的心态就是最强的锦鲤！冲就完了！", "你的积极会吸引好运，保持住！", "有目标有干劲，今天效率爆表！"],
    "平静": ["内心平静是最难得的福气，享受今天的安宁吧。", "淡定从容的你，今天会有小惊喜～", "平静中自有力量，今天适合沉淀和思考。"],
    "低落": ["运势这东西跟股票一样，跌了总会涨的……", "低落的情绪只是过客，今天给自己一点温柔。", "低谷是反弹的前奏，别太苛责自己。"],
    "焦虑": ["别急别急，你的运势在加载中……99%……", "焦虑的时候先深呼吸，今天的宜忌会帮到你！", "把焦虑转化成行动力，今天做一件小事开始！"],
    "烦躁": ["水逆退散符已发送！今天的运势有惊喜哦……", "烦躁的时候适合一个人静静，运势不差。", "放松一点，今天不适合硬刚，适合躺平。"],
}

MOOD_MAP = {
    "开心": "开心", "高兴": "开心", "快乐": "开心", "爽": "开心", "happy": "开心",
    "积极": "积极", "加油": "积极", "冲": "积极", "努力": "积极",
    "平静": "平静", "淡定": "平静", "佛系": "平静", "随便": "平静",
    "低落": "低落", "难过": "低落", "伤心": "低落", "sad": "低落",
    "焦虑": "焦虑", "紧张": "焦虑", "慌": "焦虑", "急": "焦虑",
    "烦躁": "烦躁", "烦": "烦躁", "累": "烦躁", "困": "烦躁",
    "好奇": "积极", "期待": "积极", "迷茫": "低落", "无聊": "平静",
}

AUSPICIOUS = ["紫微", "天府", "天相", "天同", "天梁", "太阳", "太阴", "武曲", "天机"]
INAUSPICIOUS = ["七杀", "破军"]


def mood_category(mood):
    m = mood.strip().lower()
    for kw, cat in MOOD_MAP.items():
        if kw in m:
            return cat
    if len(mood.strip()) <= 2:
        return "平静"
    if any(w in m for w in ["好", "棒", "赞", "爱", "喜欢"]):
        return "开心"
    if any(w in m for w in ["累", "困", "烦", "糟", "烂"]):
        return "烦躁"
    return "平静"


def make_seed(name, birthday):
    return int(hashlib.sha256(f"{name}|{birthday}".encode()).hexdigest()[:8], 16)


def pick_text(val, seed, fallback):
    """从值（可能是字符串或列表）中根据seed挑一条"""
    if isinstance(val, list):
        return val[seed % len(val)]
    if isinstance(val, str):
        return val
    return fallback[seed % len(fallback)]


def stars_str(n):
    return "★" * n + "☆" * (5 - n)


def get_star(palace_map, palace_name):
    """从宫位中提取最有代表性的星曜名称"""
    p = palace_map.get(palace_name, {})
    if not p:
        return ""
    ms = p.get("主星", [])
    if ms:
        return ms[0].get("名称", "")
    # 空宫 → 借星
    if p.get("空宫") and p.get("借星"):
        borrowed = p.get("借星", [])
        if borrowed:
            return borrowed[0]
    return ""


def get_life_stars(palace_map):
    """获取命宫所有主星"""
    p = palace_map.get("命宫", {})
    if not p:
        return [], "", ""
    ms = p.get("主星", [])
    if ms:
        stars = [s.get("名称", "") for s in ms]
        return stars, stars[0], ms[0].get("亮度", "")
    if p.get("空宫") and p.get("借星"):
        borrowed = p.get("借星", [])
        return borrowed, borrowed[0] if borrowed else "", ""
    return [], "", ""


def has_bad_love(love_p):
    """检查夫妻宫是否有煞星或化忌"""
    if not love_p:
        return False
    for s in love_p.get("主星", []):
        if s.get("四化") == "化忌":
            return True
    if love_p.get("煞星"):
        return True
    return False


def generate_fortune(name, birthday, mood):
    seed = make_seed(name, birthday)
    rng = random.Random(seed)
    mcat = mood_category(mood)
    mood_seed = sum(ord(c) for c in mood)

    astro = fetch_astrology(birthday)

    if astro:
        base_info = astro.get("基础", {})
        palaces = astro.get("十二宫", [])
        four_trans = astro.get("本命四化", {})

        palace_map = {}
        for p in palaces:
            pname = p.get("宫名", "")
            if pname:
                palace_map[pname] = p

        # 命宫分析
        life_stars, main_star, brightness = get_life_stars(palace_map)

        # 各宫星曜
        career_star = get_star(palace_map, "官禄")
        wealth_star = get_star(palace_map, "财帛")
        love_star = get_star(palace_map, "夫妻")
        love_p = palace_map.get("夫妻", {})
        love_bad = has_bad_love(love_p)

        ###### 计算运势星级 ######
        rating = 3
        if main_star in AUSPICIOUS:
            rating += 1
        elif main_star in INAUSPICIOUS:
            rating -= 1
        if brightness in ["庙", "旺"]:
            rating += 1
        elif brightness in ["陷"]:
            rating -= 1
        # 四化
        for trans_info in four_trans.values():
            if isinstance(trans_info, dict):
                tp = trans_info.get("宫", "")
                if "化禄" in str(trans_info) and tp in ["命宫", "财帛"]:
                    rating += 1
                if "化忌" in str(trans_info) and tp in ["命宫", "夫妻", "财帛"]:
                    rating -= 1
        rating = max(2, min(5, rating))
        star_icon = stars_str(rating)

        # 人格解读
        info = STAR_PERSONALITY.get(main_star, ("", ["命运自成一格，与众不同。"], 3))
        yunshi_desc = pick_text(info[1], seed + mood_seed, ["命运自成一格，与众不同。"])
        yunshi_mods = YUNSHI_MODS.get(mcat, ["运势平稳。"])
        yunshi_mod = yunshi_mods[mood_seed % len(yunshi_mods)]
        line_yunshi = f"🌟 今日综合运势：{yunshi_desc} {star_icon} {yunshi_mod}"

        # 事业
        career_val = STAR_CAREER.get(career_star, GENERAL_CAREER)
        line_career = "💼 事业/学业运：" + pick_text(career_val, seed + mood_seed, GENERAL_CAREER)

        # 财运
        wealth_val = STAR_WEALTH.get(wealth_star, GENERAL_WEALTH)
        line_wealth = "💰 财运：" + pick_text(wealth_val, seed + mood_seed + 555, GENERAL_WEALTH)

        # 桃花
        love_val = STAR_LOVE.get(love_star, GENERAL_LOVE)
        line_love = "💕 桃花运：" + pick_text(love_val, seed + mood_seed + 333, GENERAL_LOVE)
        if love_bad:
            line_love += " 💡今天遇到心动对象可以多观察，别太快上头～"

        # 心情加持
        boosts = MOOD_BOOST.get(mcat, ["🌟 今天运势不错，保持好心情！"])
        line_mood = "📿 " + rng.choice(boosts)

        # 宜/忌 —— 用心情做偏移，不同心情不同结果
        shuffled_do = DO_ACTIONS[:]
        shuffled_dont = DONT_ACTIONS[:]
        rng_do = random.Random(seed + mood_seed)
        rng_dont = random.Random(seed + mood_seed + 777)
        rng_do.shuffle(shuffled_do)
        rng_dont.shuffle(shuffled_dont)
        mood_offset = mood_seed % 20
        do_items = [shuffled_do[mood_offset % len(shuffled_do)], shuffled_do[(mood_offset + 7) % len(shuffled_do)]]
        dont_items = [shuffled_dont[(mood_offset + 3) % len(shuffled_dont)], shuffled_dont[(mood_offset + 11) % len(shuffled_dont)]]

        line_do = "✅ 宜：" + "，".join(do_items)
        line_dont = "❌ 忌：" + "，".join(dont_items)

        result = "\n".join([line_yunshi, line_career, line_love, line_wealth, line_do, line_dont, line_mood])

    else:
        # 离线模式
        result = offline_fortune(name, birthday, mood, mcat, rng)

    return result


def offline_fortune(name, birthday, mood, mcat, rng):
    """离线算命（FateStar API 不可用时）"""
    dt = datetime.strptime(birthday, "%Y-%m-%d")
    zodiac = ["猴", "鸡", "狗", "猪", "鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊"]
    animal = zodiac[dt.year % 12]

    mood_seed = sum(ord(c) for c in mood)
    seed = make_seed(name, birthday)

    star_pool = list(STAR_PERSONALITY.keys())
    fake_star = rng.choice(star_pool[:6])
    info = STAR_PERSONALITY.get(fake_star, ("", ["命运自成一格，与众不同。"], 3))

    rating = rng.randint(3, 5)
    star_icon = stars_str(rating)

    boosts = MOOD_BOOST.get(mcat, ["🌟 今天运势不错，保持好心情！"])
    mood_line = rng.choice(boosts)

    yunshi_desc = pick_text(info[1], seed + mood_seed, ["命运自成一格，与众不同。"])
    yunshi_mods = YUNSHI_MODS.get(mcat, ["运势平稳。"])
    yunshi_mod = yunshi_mods[mood_seed % len(yunshi_mods)]
    line_yunshi = f"🌟 今日综合运势：{animal}年当值，{yunshi_desc} {star_icon} {yunshi_mod}"

    ckeys = list(STAR_CAREER.keys())
    wkeys = list(STAR_WEALTH.keys())
    lkeys = list(STAR_LOVE.keys())

    career_val = STAR_CAREER[rng.choice(ckeys[:8])]
    wealth_val = STAR_WEALTH[rng.choice(wkeys[:8])]
    love_val = STAR_LOVE[rng.choice(lkeys[:8])]

    line_career = "💼 事业/学业运：" + pick_text(career_val, seed + mood_seed, GENERAL_CAREER)
    line_wealth = "💰 财运：" + pick_text(wealth_val, seed + mood_seed + 555, GENERAL_WEALTH)
    line_love = "💕 桃花运：" + pick_text(love_val, seed + mood_seed + 333, GENERAL_LOVE)

    # 宜/忌 —— 用心情做偏移，不同心情不同结果
    mood_seed = sum(ord(c) for c in mood)
    shuffled_do = DO_ACTIONS[:]
    shuffled_dont = DONT_ACTIONS[:]
    rng_do = random.Random(make_seed(name, birthday) + mood_seed)
    rng_dont = random.Random(make_seed(name, birthday) + mood_seed + 777)
    rng_do.shuffle(shuffled_do)
    rng_dont.shuffle(shuffled_dont)
    mood_offset = mood_seed % 20
    do_items = [shuffled_do[mood_offset % len(shuffled_do)], shuffled_do[(mood_offset + 7) % len(shuffled_do)]]
    dont_items = [shuffled_dont[(mood_offset + 3) % len(shuffled_dont)], shuffled_dont[(mood_offset + 11) % len(shuffled_dont)]]
    line_do = "✅ 宜：" + "，".join(do_items)
    line_dont = "❌ 忌：" + "，".join(dont_items)
    line_mood = "📿 " + mood_line

    return "\n".join([line_yunshi, line_career, line_love, line_wealth, line_do, line_dont, line_mood])


# ============================================================
# HTML 前端页面
# ============================================================

PAGE_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>玄不救非 - AI算命大师</title>
<style>
  :root {
    --bg: #0a0012; --card-bg: rgba(20, 5, 40, 0.92);
    --purple: #9b30ff; --gold: #f0c040; --cyan: #00e5ff;
    --text: #e0d8f0; --sub: #a090c0; --red: #ff5577; --green: #55ddaa;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    background: var(--bg); color: var(--text);
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
    overflow-x: hidden;
  }
  .stars { position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:0; }
  .star {
    position:absolute; background:white; border-radius:50%;
    animation:twinkle var(--dur) ease-in-out infinite; animation-delay:var(--delay);
    opacity:0;
  }
  @keyframes twinkle {
    0%,100% { opacity:0.2; transform:scale(1); } 50% { opacity:1; transform:scale(1.8); }
  }
  .container { position:relative; z-index:1; width:100%; max-width:520px; margin:20px; }
  .card {
    background:var(--card-bg); border:1px solid rgba(155,48,255,0.3);
    border-radius:20px; padding:32px 28px; backdrop-filter:blur(10px);
    box-shadow:0 0 60px rgba(155,48,255,0.15);
  }
  .title { text-align:center; margin-bottom:6px; }
  .title .icon-row { font-size:28px; letter-spacing:4px; animation:float 3s ease-in-out infinite; }
  .title h1 {
    font-size:22px; font-weight:700;
    background:linear-gradient(135deg,#c77dff,#9b30ff,#7b2fff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  }
  .title .sub { font-size:13px; color:var(--sub); margin-top:2px; }
  .title .badge {
    display:inline-block; margin-top:6px; padding:3px 12px; border-radius:20px;
    font-size:11px; background:rgba(85,221,170,0.15); color:var(--green);
    border:1px solid rgba(85,221,170,0.25);
  }
  @keyframes float { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-8px); } }
  .form-group { margin-bottom:16px; }
  .form-group label { display:block; font-size:14px; color:var(--sub); margin-bottom:6px; font-weight:500; }
  .form-group input {
    width:100%; padding:12px 16px; background:rgba(255,255,255,0.05);
    border:1px solid rgba(155,48,255,0.25); border-radius:12px;
    color:var(--text); font-size:15px; outline:none; transition:all 0.3s;
  }
  .form-group input:focus { border-color:var(--purple); box-shadow:0 0 20px rgba(155,48,255,0.2); }
  .form-group input::placeholder { color:rgba(160,144,192,0.4); }
  .btn-primary {
    width:100%; padding:14px; border:none; border-radius:14px;
    font-size:17px; font-weight:600; cursor:pointer; transition:all 0.3s; letter-spacing:2px;
    background:linear-gradient(135deg,#9b30ff,#7b2fff); color:white;
    box-shadow:0 4px 24px rgba(155,48,255,0.4);
  }
  .btn-primary:hover { transform:translateY(-2px); box-shadow:0 6px 32px rgba(155,48,255,0.6); }
  .btn-primary:active { transform:scale(0.97); }
  .btn-primary:disabled { opacity:0.5; cursor:not-allowed; transform:none; }
  .btn-secondary {
    width:100%; padding:14px; border:none; border-radius:14px;
    font-size:17px; font-weight:600; cursor:pointer; transition:all 0.3s; letter-spacing:2px;
    background:rgba(255,255,255,0.06); color:var(--sub); margin-top:8px;
  }
  .btn-secondary:hover { background:rgba(255,255,255,0.12); }
  .loading { display:none; text-align:center; padding:20px 0; }
  .loading.active { display:block; }
  .crystal {
    width:60px; height:60px; margin:0 auto 12px;
    border:4px solid rgba(155,48,255,0.2); border-top-color:var(--purple);
    border-radius:50%; animation:spin 1s linear infinite;
  }
  @keyframes spin { to { transform:rotate(360deg); } }
  .loading p { color:var(--sub); font-size:14px; }
  .result { display:none; margin-top:20px; }
  .result.active { display:block; }
  .result-line {
    padding:12px 16px; margin-bottom:8px; border-radius:12px;
    background:rgba(255,255,255,0.03); border-left:3px solid var(--purple);
    font-size:15px; line-height:1.6;
    opacity:0; transform:translateY(12px);
    animation:slideIn 0.4s ease forwards;
  }
  .result-line:nth-child(1){animation-delay:0.1s;border-left-color:#f0c040}
  .result-line:nth-child(2){animation-delay:0.2s;border-left-color:#5b9eff}
  .result-line:nth-child(3){animation-delay:0.3s;border-left-color:#ff7eb6}
  .result-line:nth-child(4){animation-delay:0.4s;border-left-color:#55ddaa}
  .result-line:nth-child(5){animation-delay:0.5s;border-left-color:#00e5ff}
  .result-line:nth-child(6){animation-delay:0.6s;border-left-color:#ff5577}
  @keyframes slideIn { to { opacity:1; transform:translateY(0); } }
  .error-msg { color:#ff5577; text-align:center; padding:16px; font-size:15px; }
  .footer { text-align:center; margin-top:16px; font-size:12px; color:rgba(160,144,192,0.4); }
  @media (max-width:480px) {
    .card { padding:24px 18px; border-radius:16px; }
    .title h1 { font-size:19px; }
  }
</style>
</head>
<body>

<div class="stars" id="stars"></div>

<div class="container">
  <div class="card">
    <div class="title">
      <div class="icon-row">🔮☯🔮</div>
      <h1>玄不救非 - AI算命大师</h1>
      <div class="sub">赛博玄学 - 不正经但头头是道</div>
      <div class="badge">🆓 永久免费 | 无需注册 | 无需API Key</div>
    </div>

    <form id="fortuneForm" style="margin-top:24px">
      <div class="form-group">
        <label>📛 你的姓名</label>
        <input type="text" id="name" placeholder="请输入姓名" maxlength="20" autocomplete="off">
      </div>
      <div class="form-group">
        <label>🎂 你的生日</label>
        <input type="text" id="birthday" placeholder="YYYY-MM-DD，如 1995-08-15" maxlength="10">
      </div>
      <div class="form-group">
        <label>💬 当前心情</label>
        <input type="text" id="mood" placeholder="一句话说说现在的心情" maxlength="50">
      </div>
      <button type="submit" class="btn-primary" id="submitBtn">🔮 开 始 算 命</button>
    </form>

    <div class="loading" id="loading">
      <div class="crystal"></div>
      <p>正在连接赛博玄学网络...</p>
    </div>

    <div class="result" id="result"></div>
    <button class="btn-secondary" id="retryBtn" style="display:none">🔄 再算一次</button>
  </div>
  <div class="footer">☯ 仅供娱乐 - 你才是自己命运的主宰 - 数据源: FateStar紫微斗数API ☯</div>
</div>

<script>
(function() {
  var s = document.getElementById('stars');
  for (var i = 0; i < 80; i++) {
    var d = document.createElement('div'); d.className = 'star';
    var size = Math.random() * 3 + 1;
    d.style.cssText =
      'left:'+Math.random()*100+'%;top:'+Math.random()*100+'%;'+
      'width:'+size+'px;height:'+size+'px;'+
      '--dur:'+(Math.random()*3+2)+'s;--delay:'+(Math.random()*5)+'s;';
    s.appendChild(d);
  }
})();

var form = document.getElementById('fortuneForm');
var loading = document.getElementById('loading');
var result = document.getElementById('result');
var submitBtn = document.getElementById('submitBtn');
var retryBtn = document.getElementById('retryBtn');

form.addEventListener('submit', function(e) {
  e.preventDefault();
  var name = document.getElementById('name').value.trim();
  var birthday = document.getElementById('birthday').value.trim();
  var mood = document.getElementById('mood').value.trim();

  if (!name || !birthday || !mood) {
    result.className = 'result active';
    result.innerHTML = '<div class="error-msg">⚠ 姓名、生日、心情都要填哦～</div>';
    retryBtn.style.display = 'block';
    return;
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(birthday)) {
    result.className = 'result active';
    result.innerHTML = '<div class="error-msg">⚠ 日期格式不对，请用 YYYY-MM-DD</div>';
    retryBtn.style.display = 'block';
    return;
  }

  result.className = 'result'; result.innerHTML = '';
  retryBtn.style.display = 'none';
  loading.classList.add('active');
  submitBtn.disabled = true;

  fetch('/api/fortune', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({name:name, birthday:birthday, mood:mood})
  }).then(function(r){return r.json()}).then(function(data){
    loading.classList.remove('active');
    submitBtn.disabled = false;
    result.className = 'result active';
    if (data.error) {
      result.innerHTML = '<div class="error-msg">⚠ ' + escapeHtml(data.error) + '</div>';
    } else {
      var html = '';
      var lines = data.result.trim().split('\n');
      lines.forEach(function(line) {
        var t = line.trim();
        if (t) html += '<div class="result-line">' + escapeHtml(t) + '</div>';
      });
      result.innerHTML = html;
    }
    retryBtn.style.display = 'block';
  }).catch(function(){
    loading.classList.remove('active');
    submitBtn.disabled = false;
    result.className = 'result active';
    result.innerHTML = '<div class="error-msg">⚠ 网络开小差了，请检查网络后重试</div>';
    retryBtn.style.display = 'block';
  });
});

retryBtn.addEventListener('click', function(){
  result.className = 'result'; result.innerHTML = '';
  retryBtn.style.display = 'none';
  form.reset();
  document.getElementById('name').focus();
});

function escapeHtml(text) {
  var d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}
</script>
</body>
</html>"""


# ============================================================
# Flask 路由
# ============================================================

@app.route("/")
def index():
    return PAGE_HTML


@app.route("/api/fortune", methods=["POST"])
def api_fortune():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    birthday = (data.get("birthday") or "").strip()
    mood = (data.get("mood") or "").strip()

    if not name:
        return jsonify({"error": "姓名不能为空"}), 400
    if len(name) > 20:
        return jsonify({"error": "名字太长啦，20字以内哦"}), 400
    if not birthday:
        return jsonify({"error": "生日不能为空"}), 400
    try:
        datetime.strptime(birthday, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "日期格式不对，请用 YYYY-MM-DD，如 1995-08-15"}), 400
    if not mood:
        return jsonify({"error": "说说现在的心情嘛～"}), 400
    if len(mood) > 50:
        return jsonify({"error": "心情描述50字以内就行啦"}), 400

    try:
        result = generate_fortune(name, birthday, mood)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": f"算命出错：{e}"}), 500


# ============================================================
# 启动逻辑
# ============================================================

def find_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        return s.getsockname()[1]


def get_local_ip():
    """获取本机局域网IP"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def main():
    port = find_port()
    local_ip = get_local_ip()
    local_url = f"http://127.0.0.1:{port}"
    lan_url = f"http://{local_ip}:{port}"

    print(f"\n  {'='*50}")
    print(f"  🔮  玄不救非 - AI算命大师")
    print(f"  {'='*50}")
    print(f"")
    print(f"  💻 本机打开: {local_url}")
    print(f"  📱 手机打开: {lan_url}")
    print(f"")
    print(f"  📡 数据源: FateStar紫微斗数API (免费/无需认证)")
    print(f"  🆓 零配置 | 无需API Key | 无需注册")
    print(f"")
    print(f"  💡 手机使用: 确保手机和电脑连同一个WiFi")
    print(f"      然后在手机浏览器输入上面的「手机打开」地址")
    print(f"  {'='*50}\n")

    def _open():
        webbrowser.open(local_url)
    threading.Timer(0.8, _open).start()

    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n  ⚠ 启动失败：{e}")
        if getattr(sys, "frozen", False):
            input("\n  按回车键退出...")
        sys.exit(1)
