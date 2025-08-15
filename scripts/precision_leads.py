import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import os
import re

class PrecisionLeadIntelligence:
    def __init__(self):
        # Your Feedly Pro access token (fresh token)
        self.feedly_access_token = "eyJraWQiOiJhdXQiLCJ2IjoiMSIsImFsZyI6ImRpciIsImVuYyI6IkEyNTZHQ00ifQ..5zpU8IXOd2kWPJTW.3zSPbXJzfb8IlBEhz29IgyxZbYHP3sedFRQYWklsqConiFabBc5WBkMazmQ8Tx9JMZc-e7BBMRwAJGW_aMtBTFEiaWbUaJlaKyEMha9jK-TiLJQjJkk6rHRSQ_Tn51766wgnR0iRAAC1jp5IF5GTRJroEiKXlAK52U2xLVBN3R8wE6aNFthA2_wcfOLYEOC3lq5YrqY5ufGHzzvTdEXNOA53RAjjv_gdcKeiuTO5XRfQWQd7Fw.7dwB9XIxgcJyT05QC6xEIg"
        
        # Claude API key
        self.claude_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.claude_api_base = "https://api.anthropic.com/v1/messages"
        self.feedly_api_base = "https://cloud.feedly.com/v3"
        
        # Refined target criteria based on consultation
        self.target_profile = {
            "company_size": "Up to 100 employees, typically 5-30",
            "key_disqualifier": "NO internal HR or recruitment function",
            "geographic_focus": "UK and Ireland (Scotland preferred for in-person work)",
            "company_age": "Typically 2-15 years old", 
            "decision_makers": ["Founder", "CEO", "Operations Manager", "COO"],
            "service_model": "Embedded/fractional talent team (2-20 days/month)",
            "timing": "Contact within 1 week of growth trigger"
        }
        
        # Enhanced growth trigger detection (refined for embedded talent opportunities)
        self.growth_triggers = {
            # Funding stages that indicate growth but not over-establishment
            'funding_signals': {
                'positive': ['seed round', 'series a', 'pre-series a', '£500k', '£1m', '£2m', '£3m',
                           'angel investment', 'crowdfunding', 'first funding', 'investment round',
                           'raised £', 'funding boost', 'seed funding', 'venture capital', 'pre-seed'],
                'negative': ['series c', 'series d', '£50m+', '£100m+', 'ipo', 'nasdaq', 'acquisition',
                           '£20m+', '£30m+']  # Added lower thresholds for "too big"
            },
            
            # Direct founder pain signals (highest value)
            'founder_struggles': ['founder hiring', 'struggling to hire', 'finding talent', 
                                'recruitment challenges', 'hiring is hard', 'can\'t find good people', 
                                'talent shortage', 'skills gap', 'hard to recruit', 'recruitment headache',
                                'spending too much time hiring', 'hiring taking forever'],
            
            # Team growth indicators (high value for embedded services)
            'team_growth': ['first employee', 'first hire', 'expanding team', 'doubling headcount', 
                          'team of 5', 'team of 10', 'team of 15', 'small team growing',
                          'hiring their first', 'building a team', 'growing the team'],
            
            # Professional development signals (perfect for embedded approach)
            'professionalizing': ['first cto', 'first commercial director', 'head of', 'first senior',
                                'leadership team', 'professionalizing', 'scaling operations',
                                'building processes', 'first management hire'],
            
            # Product/market validation (good timing for talent needs)
            'business_validation': ['product launch', 'new product', 'first major client', 
                                  'breakthrough deal', 'commercial launch', 'going live',
                                  'beta success', 'pilot programme', 'first contract'],
            
            # Organic growth signals (ideal candidates)
            'organic_growth': ['bootstrapped', 'profitable', 'self-funded', 'organic growth',
                             'revenue growth', 'customer growth', 'breaking even', 'cash positive'],
            
            # Office/location changes (but UK focused)
            'uk_expansion': ['new uk office', 'london office', 'manchester office', 'edinburgh office',
                           'glasgow office', 'uk expansion', 'bigger office', 'relocated in uk',
                           'new premises', 'office move']
        }
        
        # Negative indicators (companies probably too big/advanced)
        self.disqualifiers = {
            'too_established': ['hr director', 'hr manager', 'people director', 'talent director',
                              'head of people', 'head of hr', 'recruitment manager', 'internal hr',
                              'hr team', 'people team', 'talent team'],
            
            'too_big': ['100+ employees', '200+ team', '500+ staff', 'enterprise', 'plc',
                       'multinational', 'listed company', 'ftse', 'fortune'],
            
            'wrong_stage': ['series c', 'series d', 'pre-ipo', 'acquisition', 'merger',
                          'exit strategy', 'going public']
        }
        
        # Geographic scoring (higher scores for preferred locations)
        self.geographic_scoring = {
            'scotland': 3,      # Highest priority - can work in person
            'edinburgh': 3,
            'glasgow': 3,
            'aberdeen': 3,
            'dundee': 3,
            'london': 2,        # Good but requires travel planning
            'manchester': 2,
            'birmingham': 2,
            'leeds': 2,
            'bristol': 2,
            'ireland': 2,       # Within scope
            'dublin': 2,
            'uk': 1,           # General UK mentions
            'britain': 1,
            'northern england': 1,
            'wales': 1
        }
    
    def analyze_article_with_claude(self, article: Dict) -> Dict:
        """
        Send individual article to Claude for precise analysis
        """
        if not self.claude_api_key:
            return self.simulate_precision_analysis(article)
        
        prompt = f"""You are an expert business analyst for a Scottish embedded talent consultancy. Analyze this article to determine if the company mentioned is a good prospect.

TARGET PROFILE:
- Company size: 5-100 employees (ideally 5-30)
- Key requirement: NO internal HR or recruitment function
- Geographic: UK/Ireland (Scotland preferred)
- Growth stage: Successful but still founder-led
- Service: Embedded/fractional talent team (we become part of their team)

ARTICLE:
Title: {article['title']}
Source: {article['source']}
Summary: {article['summary']}
URL: {article['url']}

ANALYSIS REQUIRED:
1. Is there a specific company mentioned? (Name and brief description)
2. Estimated company size and likelihood they lack internal HR (High/Medium/Low confidence)
3. Growth trigger significance (funding amount, expansion details, hiring challenges)
4. Geographic location and accessibility for in-person work
5. Decision maker signals (founder mentioned, leadership team, etc.)
6. Timeline urgency (how fresh is this opportunity?)
7. Overall prospect score: EXCELLENT/GOOD/POOR and reasoning

SPECIFIC FOCUS:
- Look for companies in "growing pains" phase
- Founder still heavily involved in operations
- Growth without sophisticated infrastructure
- Any hiring challenges or talent needs mentioned
- Signs they're outgrowing founder's network/capabilities

Provide specific, actionable analysis focused on whether this company would value embedded talent support."""

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.claude_api_key,
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': 'claude-3-sonnet-20240229',
            'max_tokens': 1000,
            'messages': [{'role': 'user', 'content': prompt}]
        }
        
        try:
            response = requests.post(self.claude_api_base, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return {
                    'claude_analysis': result['content'][0]['text'],
                    'processing_method': 'Claude API'
                }
            else:
                return self.simulate_precision_analysis(article)
        except Exception as e:
            print(f"Claude API error: {e}")
            return self.simulate_precision_analysis(article)
    
    def simulate_precision_analysis(self, article: Dict) -> Dict:
        """
        Enhanced simulation based on refined criteria
        """
        title_text = article['title'].lower()
        summary_text = article['summary'].lower()
        combined_text = title_text + ' ' + summary_text
        
        analysis = {
            'company_identified': False,
            'size_confidence': 'Low',
            'growth_trigger_score': 0,
            'geographic_score': 0,
            'disqualifier_flags': [],
            'prospect_quality': 'POOR',
            'processing_method': 'Enhanced Simulation'
        }
        
        # Look for specific company mentions (improved patterns)
        company_patterns = [
            r'([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+(?:\s+Ltd|\s+Limited)?)',  # Two+ capitalised words
            r'([A-Z][a-zA-Z]+(?:Tech|Solutions|Systems|Group|Ltd|Limited))',  # Tech company patterns
            r'([A-Z][a-zA-Z]*[A-Z][a-zA-Z]*)',  # CamelCase names (StartupName)
            r'((?:[A-Z][a-z]+\s+){1,2}(?:raises|secures|announces|launches))',  # Company + action
        ]
        
        company_found = False
        for pattern in company_patterns:
            matches = re.findall(pattern, article['title'] + ' ' + article['summary'])
            if matches:
                # Filter out common non-company words
                excluded_words = ['The', 'This', 'That', 'And', 'But', 'When', 'How', 'Why', 'What', 'Where']
                valid_matches = [match for match in matches if not any(word in match for word in excluded_words)]
                if valid_matches:
                    analysis['company_identified'] = True
                    company_found = True
                    break
        
        # Growth trigger scoring (more generous for actual triggers)
        trigger_score = 0
        for category, keywords in self.growth_triggers.items():
            if isinstance(keywords, dict):
                # Funding signals have positive and negative
                for keyword in keywords['positive']:
                    if keyword in combined_text:
                        trigger_score += 2
                for keyword in keywords.get('negative', []):
                    if keyword in combined_text:
                        trigger_score -= 3  # Penalty for being too big
            else:
                # Other categories - give different weights based on relevance
                category_weight = 1
                if category == 'founder_struggles':
                    category_weight = 3  # Highest value
                elif category in ['team_growth', 'professionalizing']:
                    category_weight = 2  # High value
                
                for keyword in keywords:
                    if keyword in combined_text:
                        trigger_score += category_weight
        
        analysis['growth_trigger_score'] = trigger_score
        
        # Geographic relevance
        for location, score in self.geographic_scoring.items():
            if location in combined_text:
                analysis['geographic_score'] = max(analysis['geographic_score'], score)
        
        # Check for disqualifiers
        for category, keywords in self.disqualifiers.items():
            for keyword in keywords:
                if keyword in combined_text:
                    analysis['disqualifier_flags'].append(f"{category}: {keyword}")
        
        # Size confidence assessment (improved detection)
        size_indicators = {
            'definitely_small': ['startup', 'founded this year', 'founded 2023', 'founded 2024', 
                               'co-founder', 'bootstrap', 'early stage', 'small team', 'team of 3',
                               'team of 5', 'team of 8', 'first employee', 'hiring their first'],
            'probably_small': ['growing team', 'expanding', 'scaling', 'young company', 
                             'emerging', 'new business', 'recent launch'],
            'probably_medium': ['established', 'growing business', 'successful company', 
                              'expanding operations', 'team of 20', 'team of 30'],
            'definitely_large': ['enterprise', '100+ employees', '200+ team', '500+ staff', 
                               'multinational', 'listed company', 'ftse', 'plc', 'corporation']
        }
        
        size_confidence_score = 0
        for size_cat, indicators in size_indicators.items():
            for indicator in indicators:
                if indicator in combined_text:
                    if size_cat == 'definitely_small':
                        analysis['size_confidence'] = 'High'
                        size_confidence_score = 3
                    elif size_cat == 'probably_small':
                        analysis['size_confidence'] = 'Medium'
                        size_confidence_score = max(size_confidence_score, 2)
                    elif size_cat == 'probably_medium':
                        if size_confidence_score < 2:
                            analysis['size_confidence'] = 'Medium'
                            size_confidence_score = 1
                    else:  # definitely_large
                        analysis['size_confidence'] = 'Low'
                        analysis['disqualifier_flags'].append('definitely_too_big')
                        size_confidence_score = -2
        
        # Overall prospect scoring (refined for embedded talent focus)
        total_score = analysis['growth_trigger_score'] + analysis['geographic_score'] + size_confidence_score
        
        # Bonus points for specific embedded talent opportunities
        embedded_bonus = 0
        if 'founder_struggles' in [k for k, v in self.growth_triggers.items() if any(word in combined_text for word in v if isinstance(v, list))]:
            embedded_bonus += 3  # High value - direct pain point
        if 'team_growth' in [k for k, v in self.growth_triggers.items() if any(word in combined_text for word in v if isinstance(v, list))]:
            embedded_bonus += 2  # Good value - growing team needs
        if 'professionalizing' in [k for k, v in self.growth_triggers.items() if any(word in combined_text for word in v if isinstance(v, list))]:
            embedded_bonus += 2  # Good value - ready for professional help
        
        total_score += embedded_bonus
        
        # Company identification bonus
        if analysis['company_identified']:
            total_score += 1
        
        # Heavy penalty for disqualifiers
        total_score -= (5 * len(analysis['disqualifier_flags']))
        
        # Balanced scoring thresholds (not too strict)
        if total_score >= 6 and not analysis['disqualifier_flags'] and analysis['size_confidence'] in ['High', 'Medium']:
            analysis['prospect_quality'] = 'EXCELLENT'
        elif total_score >= 3 and len(analysis['disqualifier_flags']) <= 1:
            analysis['prospect_quality'] = 'GOOD'
        elif total_score >= 1 and not analysis['disqualifier_flags']:
            analysis['prospect_quality'] = 'GOOD'  # Give benefit of doubt to clean prospects
        else:
            analysis['prospect_quality'] = 'POOR'
        
        return analysis
    
    def generate_precision_briefing(self, articles: List[Dict], analyzed_leads: List[Dict]) -> str:
        """
        Generate targeted briefing focused on embedded talent opportunities
        """
        excellent_leads = [lead for lead in analyzed_leads if lead['analysis']['prospect_quality'] == 'EXCELLENT']
        good_leads = [lead for lead in analyzed_leads if lead['analysis']['prospect_quality'] == 'GOOD']
        
        timestamp = datetime.now().strftime('%d %B %Y at %H:%M')
        
        briefing = f"""
🎯 PRECISION LEAD INTELLIGENCE - EMBEDDED TALENT OPPORTUNITIES
{timestamp}
================================================================

📊 ANALYSIS SUMMARY:
• Total articles scanned: {len(articles)}
• Companies analyzed: {len(analyzed_leads)}
• EXCELLENT prospects: {len(excellent_leads)}
• GOOD prospects: {len(good_leads)}
• Target: Growing companies WITHOUT internal HR teams

🏆 EXCELLENT PROSPECTS (Immediate Action Required):
"""
        
        if not excellent_leads:
            briefing += "❌ No excellent prospects found today.\n"
        else:
            for i, lead in enumerate(excellent_leads, 1):
                article = lead['article']
                analysis = lead['analysis']
                
                briefing += f"""
PROSPECT {i}: {article['title']}
🔥 EXCELLENT MATCH

📍 Source: {article['source']}
🏢 Size confidence: {analysis['size_confidence']}
📈 Growth trigger score: {analysis['growth_trigger_score']}/10
🌍 Geographic fit: {analysis['geographic_score']}/3 (Scotland preferred)

💡 EMBEDDED TALENT OPPORTUNITY:
Based on growth signals, this company is likely in the "founder overwhelm" phase where they need professional talent support but don't have internal resources.

🎯 POSITIONING APPROACH:
"I noticed your [specific growth trigger]. Companies at this stage often find that talent acquisition becomes a major founder bottleneck. We specialize in embedding with growing companies like yours - becoming part of your team rather than an external agency. This typically means better cultural fit and more strategic hiring. Would be interested to understand your current talent challenges and whether our embedded approach might add value."

📋 RESEARCH CHECKLIST:
✓ LinkedIn company page - verify team size and roles
✓ Check for ANY HR/talent roles (immediate disqualifier)
✓ Identify decision maker (founder/CEO/COO)
✓ Recent job postings quality (bad adverts = opportunity)
✓ Company culture/values alignment opportunities
✓ Mutual connection possibilities

⏰ CONTACT TIMING: Within 1 week (while growth trigger is fresh)
🔗 URL: {article['url']}

---
"""
        
        briefing += f"\n🟡 GOOD PROSPECTS (Research & Validate):\n"
        
        if not good_leads:
            briefing += "• No good prospects requiring follow-up research today.\n"
        else:
            for lead in good_leads[:3]:  # Top 3 good prospects
                article = lead['article']
                analysis = lead['analysis']
                
                briefing += f"""
• {article['title']}
  Size confidence: {analysis['size_confidence']} | Geographic: {analysis['geographic_score']}/3
  Action: Research to confirm no internal HR function
  URL: {article['url']}
"""
        
        briefing += f"""

🚨 QUALIFICATION REMINDERS:
• KEY DISQUALIFIER: Any mention of HR Manager/Director/Team = NO
• IDEAL SIZE: 5-30 employees (up to 100 acceptable)
• GROWTH STAGE: Successful but still founder-led operations
• DECISION MAKERS: Founder, CEO, Operations Manager, COO
• GEOGRAPHIC: Scotland ideal, UK/Ireland acceptable

📈 EMBEDDED TALENT VALUE PROPOSITION:
"We don't just find people - we become part of your team. 2-20 days per month, embedded in your culture and values, building talent strategy aligned with your growth targets. Proactive rather than reactive."

🎯 SUCCESS PATTERN (based on 5 years organic growth):
• Companies value the embedded approach over traditional agencies
• Founder spending too much time on recruitment = perfect timing
• Just professionalizing processes = ready for talent strategy
• Expanding beyond founder's network = need our expertise

💼 NEXT ACTIONS:
1. Research EXCELLENT prospects immediately (LinkedIn, company website)
2. Disqualify any with existing HR functions
3. Identify warm introduction paths
4. Craft personalized outreach emphasizing embedded model
5. Schedule follow-up for GOOD prospects after validation

================================================================
Ready for targeted outreach to growing companies that need embedded talent support! 🎯
"""
        
        return briefing
    
    def run_precision_analysis(self):
        """
        Run the precision-targeted lead intelligence system
        """
        print("🎯 PRECISION LEAD INTELLIGENCE - EMBEDDED TALENT FOCUS")
        print("=" * 65)
        print(f"Analysis started: {datetime.now().strftime('%d %B %Y at %H:%M')}")
        print("🏆 Target: Growing companies WITHOUT internal HR teams\n")
        
        # Get articles from enhanced sources
        print("📰 Fetching from specialized business sources...")
        articles = self.get_enhanced_articles()
        
        if not articles:
            print("❌ No articles found. Check Feedly connection.")
            return
        
        print(f"✅ Retrieved {len(articles)} articles for precision analysis\n")
        
        # Analyze each article for embedded talent opportunities
        print("🔍 Running precision analysis for embedded talent prospects...")
        analyzed_leads = []
        
        for i, article in enumerate(articles):
            if i % 10 == 0:
                print(f"   Analyzed {i}/{len(articles)} articles...")
            
            analysis = self.analyze_article_with_claude(article)
            
            # Only include prospects with some potential
            if analysis.get('prospect_quality', 'POOR') in ['EXCELLENT', 'GOOD']:
                analyzed_leads.append({
                    'article': article,
                    'analysis': analysis
                })
        
        print(f"✅ Found {len(analyzed_leads)} qualified prospects\n")
        
        # Generate precision briefing
        briefing = self.generate_precision_briefing(articles, analyzed_leads)
        
        print(briefing)
        
        # Save analysis
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"precision_embedded_talent_leads_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(briefing)
            print(f"\n📁 Analysis saved to: {filename}")
        except Exception as e:
            print(f"Could not save analysis: {e}")
        
        print(f"\n🎯 Focus: Companies in 'founder overwhelm' phase needing embedded talent support")
    
    def get_enhanced_articles(self, hours_back: int = 24) -> List[Dict]:
        """
        Get articles with enhanced filtering for startup/SME focus
        """
        headers = {'Authorization': f'Bearer {self.feedly_access_token}'}
        
        subscriptions_response = requests.get(f"{self.feedly_api_base}/subscriptions", headers=headers)
        
        if subscriptions_response.status_code != 200:
            return []
        
        subscriptions = subscriptions_response.json()
        
        # Target feeds most likely to have startup/SME stories
        startup_focused_feeds = [
            'Scottish Business News',
            'FutureScot', 
            'Scottish Enterprise',
            'Insider Scotland Startups',
            'Growth Business',
            'TechRound',
            'Crunchbase News',
            'UK Tech News',
            'StartupDaily UK'
        ]
        
        all_articles = []
        
        for subscription in subscriptions:
            title = subscription.get('title', '')
            
            # More precise matching for startup/SME focused feeds
            if (any(target in title for target in startup_focused_feeds) or 
                any(keyword in title.lower() for keyword in ['startup', 'small business', 'sme', 'entrepreneur'])):
                
                print(f"📈 Startup/SME feed: {title}")
                
                since_timestamp = int((datetime.now() - timedelta(hours=hours_back)).timestamp() * 1000)
                
                params = {
                    'streamId': subscription.get('id', ''),
                    'count': 12,  # Slightly fewer per feed for quality over quantity
                    'newerThan': since_timestamp
                }
                
                articles_response = requests.get(
                    f"{self.feedly_api_base}/streams/contents",
                    headers=headers,
                    params=params
                )
                
                if articles_response.status_code == 200:
                    data = articles_response.json()
                    items = data.get('items', [])
                    
                    for item in items:
                        article = {
                            'title': item.get('title', 'No title'),
                            'summary': item.get('summary', {}).get('content', 'No summary available')[:800],
                            'url': item.get('originId', ''),
                            'published': item.get('published', ''),
                            'source': title
                        }
                        all_articles.append(article)
        
        return all_articles

if __name__ == "__main__":
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  Running in enhanced simulation mode")
        print("For full Claude API analysis, set ANTHROPIC_API_KEY environment variable\n")
    
    system = PrecisionLeadIntelligence()
    system.run_precision_analysis()