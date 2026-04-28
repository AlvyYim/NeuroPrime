"""
生成UI界面预览图
使用matplotlib绘制UI原型示意图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def draw_ui_mockup():
    """绘制UI界面原型图"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 1600)
    ax.set_ylim(0, 1000)
    ax.axis('off')
    
    # 背景
    ax.add_patch(Rectangle((0, 0), 1600, 1000, facecolor='#f5f5f5', edgecolor='none'))
    
    # 1. 顶部RibbonBar
    ax.add_patch(Rectangle((0, 920), 1600, 80, facecolor='#f0f0f0', edgecolor='#cccccc', linewidth=2))
    
    # Home按钮
    ax.add_patch(FancyBboxPatch((10, 930), 80, 60, boxstyle="round,pad=5", 
                                facecolor='#e0e0e0', edgecolor='#999999'))
    ax.text(50, 960, '🏠 Home', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # RibbonBar标签页
    tabs = ['数据加载', 'Spike检测', 'Spike排序', 'LFP分析', '行为分析', '智能分析', '自定义算法']
    x_pos = 100
    for tab in tabs:
        # 标签背景
        ax.add_patch(FancyBboxPatch((x_pos, 930), 100, 60, boxstyle="round,pad=3",
                                    facecolor='white', edgecolor='#cccccc'))
        # 标签文字
        ax.text(x_pos + 50, 970, tab, ha='center', va='center', fontsize=9, color='#0078d4')
        # 按钮组
        ax.add_patch(Rectangle((x_pos + 5, 935), 90, 25, facecolor='#f9f9f9', edgecolor='#dddddd'))
        ax.text(x_pos + 50, 947, '功能按钮', ha='center', va='center', fontsize=7, color='#666666')
        x_pos += 110
    
    # 2. 左侧导航栏
    ax.add_patch(Rectangle((0, 50), 250, 870, facecolor='#f5f5f5', edgecolor='#cccccc', linewidth=2))
    ax.add_patch(Rectangle((0, 880), 250, 40, facecolor='#e0e0e0', edgecolor='#cccccc'))
    ax.text(125, 900, '📁 工程导航', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 导航树内容
    y_pos = 850
    items = [
        ('📁 猕猴V1区电生理实验', 0, True),
        ('  📂 试验1 (2024-01-15)', 20, True),
        ('    📊 电信号数据', 40, True),
        ('      ⚡ Spike数据', 60, True),
        ('        📄 时间戳', 80, False),
        ('        📄 波形', 80, False),
        ('        📄 聚类标签', 80, False),
        ('      📄 LFP信号', 60, False),
        ('    📋 行为数据', 40, True),
        ('      📄 事件', 60, False),
        ('      📄 试次', 60, False),
        ('      📄 刺激', 60, False),
        ('  📂 试验2 (2024-01-16)', 20, True),
    ]
    
    for text, indent, expandable in items:
        if y_pos > 400:
            bg_color = '#ffffff' if '试验' in text or '工程' in text else 'none'
            if bg_color != 'none':
                ax.add_patch(Rectangle((10 + indent, y_pos - 15), 230 - indent, 25, 
                                      facecolor=bg_color, edgecolor='#eeeeee', alpha=0.5))
            ax.text(15 + indent, y_pos, text, ha='left', va='center', fontsize=9)
            y_pos -= 30
    
    # 3. 右侧参数配置面板
    ax.add_patch(Rectangle((250, 50), 350, 870, facecolor='white', edgecolor='#cccccc', linewidth=2))
    ax.add_patch(Rectangle((250, 880), 350, 40, facecolor='#f0f0f0', edgecolor='#cccccc'))
    ax.text(425, 900, '⚙️ 参数配置', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 参数选项卡
    ax.add_patch(Rectangle((260, 840), 160, 30, facecolor='#e0e0e0', edgecolor='#cccccc'))
    ax.text(340, 855, '基本参数', ha='center', va='center', fontsize=10)
    ax.add_patch(Rectangle((420, 840), 160, 30, facecolor='white', edgecolor='#cccccc'))
    ax.text(500, 855, '高级参数', ha='center', va='center', fontsize=10)
    
    # 参数表单
    params = [
        ('检测方法:', '阈值检测 ▼'),
        ('阈值倍数:', '4.0'),
        ('检测通道:', '全部通道 ▼'),
        ('波形窗口:', '50 ms'),
    ]
    y_pos = 800
    for label, value in params:
        ax.text(270, y_pos, label, ha='left', va='center', fontsize=10, fontweight='bold')
        ax.add_patch(Rectangle((350, y_pos - 12), 200, 24, facecolor='white', edgecolor='#cccccc'))
        ax.text(360, y_pos, value, ha='left', va='center', fontsize=10)
        y_pos -= 50
    
    # 分析按钮
    ax.add_patch(FancyBboxPatch((300, 550), 250, 50, boxstyle="round,pad=5",
                                facecolor='#0078d4', edgecolor='#005a9e'))
    ax.text(425, 575, '🔍 开始分析', ha='center', va='center', fontsize=14, 
            fontweight='bold', color='white')
    
    # 4. 可视化区域
    ax.add_patch(Rectangle((600, 50), 1000, 870, facecolor='#fafafa', edgecolor='#cccccc', linewidth=2))
    ax.add_patch(Rectangle((600, 880), 1000, 40, facecolor='#f0f0f0', edgecolor='#cccccc'))
    ax.text(1100, 900, '📊 数据可视化', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 可视化工具栏
    tools = ['🔍+', '🔍-', '⟲ 重置', '💾 导出']
    x_pos = 1450
    for tool in reversed(tools):
        ax.add_patch(Rectangle((x_pos - 60, 885), 55, 30, facecolor='white', edgecolor='#cccccc'))
        ax.text(x_pos - 32, 900, tool, ha='center', va='center', fontsize=9)
        x_pos -= 65
    
    # 可视化内容区域（虚线框表示）
    ax.add_patch(Rectangle((620, 100), 960, 750, facecolor='white', edgecolor='#cccccc', 
                          linestyle='--', linewidth=2))
    
    # 可视化内容说明
    viz_text = """
    ┌─────────────────────────────────────────────────────────┐
    │                    🎨 可视化区域                         │
    │                                                         │
    │    这里将使用 PyQtGraph 显示：                          │
    │                                                         │
    │    • 信号波形图                                         │
    │    • Spike栅格图                                        │
    │    • PSTH直方图                                         │
    │    • 功率谱密度图                                       │
    │    • 时频图                                             │
    │    • 调谐曲线                                           │
    │    • ROC曲线                                            │
    │                                                         │
    │    支持交互操作：                                       │
    │    • 鼠标滚轮缩放                                       │
    │    • 拖拽平移                                           │
    │    • 区域选取                                           │
    │    • 数据点提示                                         │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
    """
    ax.text(1100, 475, viz_text, ha='center', va='center', fontsize=9, 
            family='monospace', color='#666666')
    
    # 状态信息
    ax.text(650, 70, '📈 采样率: 30000 Hz', ha='left', va='center', fontsize=10)
    ax.text(850, 70, '📊 通道数: 4', ha='left', va='center', fontsize=10)
    ax.text(1000, 70, '⏱️ 时长: 20.0 s', ha='left', va='center', fontsize=10)
    
    # 5. 底部状态栏
    ax.add_patch(Rectangle((0, 0), 1600, 50, facecolor='#0078d4', edgecolor='none'))
    ax.text(20, 25, '✅ 系统就绪 | 当前工程: 猕猴V1区电生理实验', 
            ha='left', va='center', fontsize=11, color='white', fontweight='bold')
    
    # 标题
    fig.suptitle('NeuroPrime - 猕猴脑电生理数据分析平台 (UI原型)', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.savefig('neuroprime_ui_preview.png', dpi=150, bbox_inches='tight', 
                facecolor='#f5f5f5', edgecolor='none')
    print("UI预览图已生成: neuroprime_ui_preview.png")
    plt.close()

if __name__ == "__main__":
    draw_ui_mockup()
