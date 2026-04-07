from typing import List, Dict

def compress_news(korean: List[Dict], us: List[Dict]) -> str:
    """AI에게 전달할 수 있도록 뉴스를 간결하게 압축"""
    lines = ["=== 오늘 주요 경제 뉴스 ==="]
    
    lines.append("\n[한국 경제]")
    for news in korean[:8]:
        lines.append(f"• {news['title']}")
        if news.get('summary'):
            lines.append(f"  {news['summary']}")
    
    lines.append("\n[미국 경제]")
    for news in us[:6]:
        lines.append(f"• {news['title']}")
        if news.get('summary'):
            lines.append(f"  {news['summary']}")
    
    return "\n".join(lines)
