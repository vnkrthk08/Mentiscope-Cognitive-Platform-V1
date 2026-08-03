"""
==========================================================
Template Engine
==========================================================
"""

import random
from uuid import uuid4

class TemplateEngine:

    @staticmethod
    def generate(template):
        module = template["module"]
        if module == "PatternBot":
            return TemplateEngine.pattern(template)
        elif module == "CompareBot":
            return TemplateEngine.compare(template)
        elif module == "VisionBot":
            return TemplateEngine.vision(template)
        elif module == "SolverBot":
            return TemplateEngine.solver(template)
        raise ValueError(f"Unknown module: {module}")

    @staticmethod
    def pattern(template):
        t_id = template['template_id']
        try:
            idx = int(t_id.split('-T')[1])
        except:
            idx = 1
        target_level = template['difficulty']
        
        data = {}
        options = []
        answer = ''
        hint = template.get('hint', '')
        
        if idx == 1:
            start = random.randint(2, 11)
            diff = random.randint(2, 5)
            seq = [start + i*diff for i in range(4)]
            answer = str(start + 4*diff)
            data = {'sequence': seq, 'type': 'arithmetic', 'difference': diff}
            options = [answer, str(int(answer)+2), str(int(answer)-diff-1), str(start*(4+diff))]
        elif idx == 2:
            start = random.randint(2, 11)
            ratio = random.randint(2, 5)
            seq = [start * (ratio**i) for i in range(4)]
            answer = str(start * (ratio**4))
            data = {'sequence': seq, 'type': 'geometric', 'ratio': ratio}
            options = [answer, str(seq[-1]+ratio), str(seq[-1]*(ratio+1)), str(seq[-1]*2)]
        else:
            start = random.randint(2, 6)
            mult = 2
            constant = 1
            seq = [start]
            for _ in range(3): seq.append(seq[-1]*mult + constant)
            answer = str(seq[-1]*mult + constant)
            data = {'sequence': seq, 'type': 'recursive', 'mult': mult, 'constant': constant}
            options = [answer, str(seq[-1]*mult), str(seq[-1]+16), str(seq[-1]*3)]
            
        random.shuffle(options)
        
        return {
            'question_id': f"{template['template_id']}-{uuid4().hex[:8]}",
            'template_id': template['template_id'],
            'module': template['module'],
            'difficulty': target_level,
            'story': random.choice(template.get('story_pool', ['Analyze sequence.'])),
            'question': f"Determine the next sequence node: [ {', '.join(map(str, data['sequence']))}, ? ]",
            'options': options,
            'correct_answer': answer,
            'hint': hint,
            'data': data
        }

    @staticmethod
    def compare(template):
        a = random.randint(10, 90)
        b = random.randint(10, 90)
        ans = str(a) if a > b else str(b) if b > a else 'Equal'
        ops = [str(a), str(b), 'Equal', 'Cannot Determine']
        random.shuffle(ops)
        
        return {
            'question_id': f"{template['template_id']}-{uuid4().hex[:8]}",
            'template_id': template['template_id'],
            'module': template['module'],
            'difficulty': template['difficulty'],
            'story': random.choice(template.get('story_pool', ['Compare reactors.'])),
            'question': 'Which reactor output is more optimal?',
            'options': ops,
            'correct_answer': ans,
            'hint': template.get('hint', ''),
            'data': {'pct1': a, 'amt1': 100, 'pct2': b, 'amt2': 100}
        }

    @staticmethod
    def vision(template):
        return {
            'question_id': f"{template['template_id']}-{uuid4().hex[:8]}",
            'template_id': template['template_id'],
            'module': template['module'],
            'difficulty': template['difficulty'],
            'story': random.choice(template.get('story_pool', ['Analyze the visual data array.'])),
            'question': 'Which node shows the highest anomaly rate?',
            'options': ['Node Alpha', 'Node Beta', 'Node Gamma', 'Node Delta'],
            'correct_answer': 'Node Beta',
            'hint': template.get('hint', ''),
            'data': {'chartType': 'bar', 'values': [12, 45, 23, 8], 'labels': ['Alpha', 'Beta', 'Gamma', 'Delta'], 'maxValue': 50}
        }

    @staticmethod
    def solver(template):
        return {
            'question_id': f"{template['template_id']}-{uuid4().hex[:8]}",
            'template_id': template['template_id'],
            'module': template['module'],
            'difficulty': template['difficulty'],
            'story': random.choice(template.get('story_pool', ['Allocate power to the nodes.'])),
            'question': 'Optimize the power grid routing avoiding obstacles.',
            'options': ['Path A', 'Path B', 'Path C', 'Path D'],
            'correct_answer': 'Path B',
            'hint': template.get('hint', ''),
            'data': {'capacityTarget': {'alpha': 40, 'beta': 40, 'gamma': 20}}
        }