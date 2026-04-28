"""
生成RibbonBar预览图 - 纯标签页模式
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def draw_ribbon_preview():
    """绘制RibbonBar预览图 - 纯标签页设计"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 5))
    ax.set_xlim(0, 1600)
    ax.set_ylim(0, 150)
    ax.axis('off')
    
    # 背景
    ax.add_patch(Rectangle((0, 0), 1600, 150, facecolor='#f5f5f5', edgecolor='#cccccc', linewidth=1))
    
    # 标签页
    tabs = [
        ("数据加载", 10, 120, True),
        ("Spike检测", 132, 120, False),
        ("Spike排序", 254, 120, False),
        ("LFP分析", 376, 100, False),
        ("行为分析", 478, 100, False),
        ("智能分析", 580, 100, False),
        ("自定义算法", 682, 120, False),
    ]
    
    for tab_name, x_pos, width, is_selected in tabs:
        if is_selected:
            # 选中的标签页
            ax.add_patch(FancyBboxPatch((x_pos, 115), width, 35, 
                                        boxstyle="round,pad=2,rounding_size=8",
                                        facecolor='#f5f5f5', edgecolor='#cccccc', 
                                        linewidth=1.5, zorder=10))
            ax.text(x_pos + width/2, 132, tab_name, ha='center', va='center', 
                   fontsize=11, fontweight='bold', color='#0078d4', zorder=11)
        else:
            # 未选中的标签页
            ax.add_patch(FancyBboxPatch((x_pos, 115), width, 35, 
                                        boxstyle="round,pad=2,rounding_size=8",
                                        facecolor='#e0e0e0', edgecolor='#cccccc', 
                                        linewidth=1, zorder=5))
            ax.text(x_pos + width/2, 132, tab_name, ha='center', va='center', 
                   fontsize=11, fontweight='bold', color='#333333', zorder=6)
    
    # 内容区域背景
    ax.add_patch(Rectangle((0, 0), 1600, 115, facecolor='#f5f5f5', edgecolor='none'))
    
    # 标签页内容区域（以"数据加载"为例）
    # 工程管理组
    group1_x = 20
    ax.add_patch(FancyBboxPatch((group1_x, 10), 240, 95, 
                                boxstyle="round,pad=3",
                                facecolor='white', edgecolor='#cccccc', linewidth=1.5))
    ax.text(group1_x + 120, 95, "工程管理", ha='center', va='center', 
           fontsize=9, fontweight='bold', color='#666666')
    
    # 按钮
    buttons1 = ["新建工程", "打开工程", "保存工程"]
    for i, btn_text in enumerate(buttons1):
        btn_x = group1_x + 15 + i * 75
        ax.add_patch(FancyBboxPatch((btn_x, 20), 65, 60, 
                                    boxstyle="round,pad=2",
                                    facecolor='#f9f9f9', edgecolor='#cccccc', linewidth=1))
        ax.text(btn_x + 32.5, 50, btn_text, ha='center', va='center', 
               fontsize=8, color='#333333')
    
    # 导入文件组
    group2_x = 280
    ax.add_patch(FancyBboxPatch((group2_x, 10), 170, 95, 
                                boxstyle="round,pad=3",
                                facecolor='white', edgecolor='#cccccc', linewidth=1.5))
    ax.text(group2_x + 85, 95, "导入文件", ha='center', va='center', 
           fontsize=9, fontweight='bold', color='#666666')
    
    buttons2 = ["导入电信号", "导入行为数据"]
    for i, btn_text in enumerate(buttons2):
        btn_x = group2_x + 15 + i * 75
        ax.add_patch(FancyBboxPatch((btn_x, 20), 65, 60, 
                                    boxstyle="round,pad=2",
                                    facecolor='#f9f9f9', edgecolor='#cccccc', linewidth=1))
        ax.text(btn_x + 32.5, 50, btn_text, ha='center', va='center', 
               fontsize=8, color='#333333')
    
    # 标题
    fig.suptitle('NeuroPrime RibbonBar 设计 - 纯标签页模式', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    # 说明文字
    ax.text(800, 5, '点击标签页切换显示对应的功能按钮组', 
           ha='center', va='bottom', fontsize=10, style='italic', color='#666666')
    
    plt.tight_layout()
    plt.savefig('ribbonbar_preview.png', dpi=150, bbox_inches='tight', 
                facecolor='#f5f5f5', edgecolor='none')
    print("RibbonBar预览图已生成: ribbonbar_preview.png")
    plt.close()

if __name__ == "__main__":
    draw_ribbon_preview()
