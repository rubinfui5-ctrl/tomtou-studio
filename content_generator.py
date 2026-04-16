#!/usr/bin/env python3
"""
Content Generator - Solomon Empire
Autonomously generates content for Instagram, Email, Blog, and other platforms
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data/generated_content")
DATA_DIR.mkdir(parents=True, exist_ok=True)

QUEUE_FILE = DATA_DIR / "content_queue.json"

CONTENT_TEMPLATES = {
    "instagram_caption": [
        "💰 Building wealth one day at a time. Today's lesson: {topic}. Follow for daily financial tips! #Solomon #Wealth #Finance",
        "🔥 Real talk about money: {topic}. Drop a ❤️ if this resonates! #FinancialFreedom #Business",
        "📈 The secret to consistent income: {topic}. Save this post! #Entrepreneur #Hustle #Success",
        "💡 Stop sleeping on {topic}. This is how I'm building my empire. #Business #SideHustle #Money",
    ],
    "email_subject": [
        "🔥 {topic} - Your path to $10K/week",
        "URGENT: {topic} opportunity closing soon",
        "How I made ${amount} with {topic}",
        "[CASE STUDY] {topic} success story",
    ],
    "email_body": [
        """Hey {name},

Quick message about {topic}.

I've been tracking the numbers and {topic} is showing massive potential right now.

Here's what you need to know:
• Key insight 1 about {topic}
• Key insight 2 about {topic}
• Action step: {action}

Don't miss this window.

Rubin
@rubinfuimaono
deals.thatsonmeandyou.com""",
    ],
    "blog_post": [
        """# {topic}: A Complete Guide

## Introduction
{topic} is one of the most powerful tools for building sustainable income in 2024.

## Key Points
1. Understanding {topic}
2. Implementing {topic} in your business
3. Scaling with {topic}

## Action Steps
- Start with small tests
- Track your results
- Scale what works

## Conclusion
{topic} can transform your business when applied consistently."""
    ]
}

TOPICS = [
    "dropshipping from AliExpress",
    "print-on-demand merchandise",
    "email marketing automation",
    "Instagram affiliate marketing",
    "digital product creation",
    "subscription box businesses",
    "Shopify store optimization",
    "social media monetization",
    "passive income streams",
    "e-commerce scaling strategies",
]


def load_queue():
    """Load content queue."""
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE) as f:
            return json.load(f)
    return {"generated": [], "pending": [], "published": []}


def save_queue(data):
    """Save content queue."""
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def generate_instagram_post(topic=None):
    """Generate an Instagram post."""
    topic = topic or random.choice(TOPICS)
    template = random.choice(CONTENT_TEMPLATES["instagram_caption"])
    caption = template.format(topic=topic)

    return {
        "id": f"ig_{int(time.time())}",
        "platform": "instagram",
        "type": "caption",
        "content": caption,
        "topic": topic,
        "hashtags": ["#Solomon", "#Wealth", "#Business", "#Finance", "#Entrepreneur"],
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }


def generate_email_campaign(topic=None):
    """Generate an email campaign."""
    topic = topic or random.choice(TOPICS)
    subject_template = random.choice(CONTENT_TEMPLATES["email_subject"])
    body_template = random.choice(CONTENT_TEMPLATES["email_body"])

    subject = subject_template.format(
        topic=topic,
        amount=random.randint(500, 5000)
    )
    body = body_template.format(
        name="{first_name}",
        topic=topic,
        action=f"Start implementing {topic} today"
    )

    return {
        "id": f"email_{int(time.time())}",
        "platform": "email",
        "type": "campaign",
        "subject": subject,
        "content": body,
        "topic": topic,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }


def generate_blog_post(topic=None):
    """Generate a blog post."""
    topic = topic or random.choice(TOPICS)
    template = random.choice(CONTENT_TEMPLATES["blog_post"])
    content = template.format(topic=topic)

    return {
        "id": f"blog_{int(time.time())}",
        "platform": "blog",
        "type": "article",
        "content": content,
        "topic": topic,
        "word_count": len(content.split()),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }


def generate_batch(count=5):
    """Generate a batch of mixed content."""
    generated = []
    generators = [generate_instagram_post, generate_email_campaign, generate_blog_post]

    for i in range(count):
        generator = generators[i % len(generators)]
        content = generator()
        generated.append(content)
        print(f"  ✓ Generated {content['platform']} content: {content['topic'][:40]}...")

    return generated


def run_generator():
    """Main content generation loop."""
    print("🚀 Content Generator starting...")

    while True:
        try:
            queue = load_queue()

            # Generate new content if queue is low
            if len(queue["pending"]) < 10:
                print(f"\n  📝 Generating content batch...")
                new_content = generate_batch(5)

                queue["generated"].extend(new_content)
                queue["pending"].extend(new_content)
                save_queue(queue)

                print(f"  ✓ Queue: {len(queue['pending'])} pending, {len(queue['published'])} published")

            print(f"  💤 Next generation in 5 minutes...")
            time.sleep(300)

        except KeyboardInterrupt:
            print("\n⏹  Content Generator stopped")
            break
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            time.sleep(30)


if __name__ == "__main__":
    run_generator()
