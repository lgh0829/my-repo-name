#from openai import OpenAI
from openai import AsyncOpenAI
import re
try:
    import win32com.client as win32
except ImportError:
    win32 = None

import json
import asyncio

HWP_SAVED_PATH = ""

class CloudDraft:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    def make_hwp(self, Data, User):
        print('make_hwp 시작')
        if win32 is None:
            print("win32com is not available. Skipping HWP creation.")
            return "HWP creation skipped (win32com missing)"

        base_dir = "C:/Users/kwoor/clouddraft/"
        FilePath = f"{base_dir}template.hwpx"
        hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
        hwp.XHwpWindows.Item(0).Visible = False
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        hwp.Open(FilePath)       

        fields = hwp.GetFieldList()
        print(fields)
        #누름틀 키 리스트
        # Data의 키 리스트
        mapping_dict = {
            "현황":"current",
            "이용목적":"purpose",
            "이용계획":"plan",
            "필요성":"necessity",
            "사업계획":"afterplan",
            "기대효과":"expected"
        }    
        mapping_dict = {
            "current":"현황",
            "purpose":"이용목적",
            "plan":"이용계획",
            "necessity":"필요성",
            "afterplan":"사업계획",
            "expected":"기대효과"
        }
        for key in mapping_dict.keys():            
            # 누름틀에 텍스트 넣기
            field_name = key
            text_to_insert = Data.get(mapping_dict[key],'기입한 내용이 없습니다.')
            text_to_insert = text_to_insert.replace('\n', '\r\n')

            if key == "BriefDescriptionOfDrawings":
                print(mapping_dict[key])
                print(text_to_insert)
            elif key == "claim":
                #print(text_to_insert)
                text_to_insert = list(text_to_insert) 
                count = 2
                for i in range(len(text_to_insert)-1):
                    if text_to_insert[i] == '¶':
                        text_to_insert[i] = f'\r\n【청구항 {count}】\r\n'
                        count += 1
                text_to_insert = ''.join(text_to_insert)
                if text_to_insert[-1] == '¶':
                    text_to_insert = text_to_insert[:-1]
            elif key == "Background":
                before_background = "."
                if text_to_insert.find('¶') != -1:
                    before_background = text_to_insert.split('¶')[0]
                    text_to_insert = text_to_insert.split('¶')[1]
                #fields = hwp.GetFieldList()
                hwp.PutFieldText('BeforePatent', before_background)
                    
            #fields = hwp.GetFieldList()
            #field_index = fields.index(field_name)
            hwp.PutFieldText(key, text_to_insert)

        # 원하는 이름으로 저장
        save_path = f"{base_dir}{User}.hwp"
        hwp.SaveAs(save_path, "HWP")
        hwp.Quit()
        print('save_path', save_path)

        return save_path

    async def search_preview(self, query):

        completion = await self.client.chat.completions.create(
            model="gpt-4o-search-preview",
            web_search_options={
                "search_context_size": "low",
                "user_location": {
                    "type": "approximate",
                    "approximate": {
                        "country": "KR",
                        "city": "Seoul",
                        "region": "Seoul",
                    }
                },
            },
            messages=[
                {
                    "role": "user",
                    "content": f"{query}가 가지고 있는 특허 전문 인력의 강점을 알려줘.",
                }
            ],
        )
        #print(completion)
        text = completion.choices[0].message.content
        cleaned_text = re.sub(r'\([^)]*\)', '', text)
        return cleaned_text

    async def make_content(self, query, id):
        example = {
"현황": 
"""1) 특허법률사무소의 기업 비즈니스 현황 및 장점
  가) 전문 인력 및 경력
  나) 서비스 강점
  다) 기업 비즈니스 현황""",

"이용목적": 
"""1) 업무 효율화 및 전문성 강화
  가) 수작업 기반 데이터 관리의 변화 필요
  나) 업무 프로세스의 혁신 도모
2) 서비스 품질 향상 및 고객 만족도 제고
  가) 법률 및 특허 데이터 보관 체계 마련
  나) 신속한 정보 공유와 협업
3) 미래 기술 대응력 확보
  가) 첨단 기술과의 연계를 위한 기반 마련
  나) 시장 변화에 유연하게 대응""",

"이용계획": """1) 클라우드 서비스 도입 단계
  가) 전환 필요성 및 우선순위 도출
  나) 전환 로드맵 수립
2) 데이터 축적 및 통합 관리
  가) 데이터 중앙 집중화
  나) 체계적 분석 및 활용 기반 마련
3) 운영 및 모니터링 체계 구축
  가) 안정적 운영
  나) 지속적 모니터링 체계 도입""",

"필요성":"""1) 비용 부담 경감
  가) 클라우드 인프라 구축 및 초기 전환 비용 지원을 통한 재정 부담 완화
  나) 장기적 운영 및 유지보수 비용에 대한 정부 보조금 및 세제 혜택 제공

2) 기술 전문성 및 교육 지원
  가) 클라우드 전환 관련 최신 기술
  나) 전문 컨설팅 및 기술 지원을 통한 내부 역량 강화

3) 정책적 뒷받침 및 안정성 확보
  가) 디지털 전환 촉진을 위한 정부 정책 및 규제 완화
  나) 혁신기업 육성을 위한 다양한 지원사업 및 인센티브 프로그램 제공""",

"사업계획":"""1) 지속 활용을 통한 혁신기업 성장 계획
  가) 클라우드 서비스 도입 및 지속 활용
  나) 정기적인 시스템 업데이트와 보안 강화
  다) 사용자 피드백을 반영한 지속적 서비스 개선 및 확장

2) 데이터 축적 및 분석 강화
  가) 다양한 데이터를 체계적으로 축적
  나) 빅데이터 분석 도구 도입으로 내부 정보 인사이트 도출 및 의사결정 지원

3) 전사 정보의 데이터화 추진
  가) 각 부서의 업무 데이터를 클라우드에 통합하여 전사적인 데이터 관리 체계 마련
  나) 업무 프로세스 디지털화를 통한 효율성 증대 및 신속한 대응 체계 구축

4) 데이터 기반 혁신기업으로의 성장
  가) 데이터 분석을 통한 전략적 의사결정 체계 확립
  나) 지속적인 기술 투자 및 정부지원 프로그램 활용으로 경쟁력 강화""",
"기대효과":"""1) 운영 효율성 및 비용 절감
  가) 기존 시스템 대비 유지보수 및 서버 운영 등 IT 비용을 크게 절감할 수 있음
  나) 클라우드 기반 자원 최적화를 통해 업무 효율성이 증대되고, 인력 및 자원의 활용도가 향상됨

2) 유연한 서비스 확장
가) 시장 변화에 따라 탄력적으로 자원을 조정할 수 있음
나) 신규 서비스 출시 및 기존 서비스 개선의 속도가 향상됨

3) 보안 및 데이터 관리 강화
가) 최신 보안 기술을 도입하여 보안 수준을 강화함
나) 중앙집중형 데이터 관리 시스템 구축으로 정보 유출 위험을 최소화함

4) 디지털 경쟁력 강화
가) 고객 맞춤형 서비스 제공 및 데이터 기반 의사결정을 통해 경쟁력을 제고함
나) 장기적으로 기업 가치 상승에 기여함
다) 예시: 모든 공정 절차를 전산화하여 실시간으로 공정 현황을 파악함으로써, 공정 효율화를 통한 매출액 20% 향상, 비용 15% 절감, 납품시간 30% 단축 등의 효과 기대""",
                }
        
        prompt = {"현황" : f"{query}가 가지고 있는 장점을 기술하면서 기업 비즈니스 현황에 대해 작성해줘. 다음 내용을 포함시켜줘. 기업 개요: 중소기업 또는 중견기업으로, 제조, 유통, IT 등 전통산업 혹은 서비스업 분야에서 일정 기간 안정적인 영업을 유지하고 있으나, 디지털 전환 및 IT 인프라 현대화가 시급한 상태입니다. 현 시스템 문제점: 기존 레거시 시스템 중심의 IT 환경으로 인해 데이터 관리, 보안, 업무 프로세스의 효율성이 떨어지며, 급변하는 시장 환경에 신속하게 대응하기 어려운 상황입니다. 경쟁력 분석: 경쟁사 대비 클라우드 기술 도입이 미흡하여, 비용 효율성, 확장성, 신속한 서비스 개선 측면에서 열세를 보이고 있습니다.",
                "이용목적": f"{query}가 가지고 있는 장점을 살리기 위한 클라우드 서비스 이용목적에 대해 작성해줘. 다음 내용을 참고하여 알맞게 변경해서 구체적으로 작성해줘. 디지털 전환: 클라우드 도입을 통해 기존의 아날로그 및 레거시 시스템을 디지털 환경으로 전환하여, 업무 자동화 및 데이터 기반 의사결정 체계를 마련합니다. 비용 효율성 강화: IT 인프라 운영 비용 절감과 자원 효율화를 도모하며, 시스템 유지보수 및 업그레이드 비용 부담을 경감합니다. 시장 경쟁력 제고: 클라우드 기반 서비스를 통해 빠른 시장 대응 및 신규 비즈니스 모델 창출, 고객 서비스 개선을 실현합니다.",
                "이용계획": f"{query}가 제대로 클라우드 서비스로 디지털 전환하기 위한 클라우드 서비스 이용계획에 대해 작성해줘. 다음 내용을 참고하여 알맞게 변경해서 구체적으로 작성해줘. 분석 및 설계 : 기존 시스템 및 업무 프로세스 진단, 클라우드 전환을 위한 전략 수립 및 파일럿 프로젝트 기획, 도입 및 전환 : 클라우드 플랫폼(퍼블릭, 프라이빗 또는 하이브리드 선택)에의 전환 작업, 데이터 마이그레이션, 시스템 통합, 보안 강화 작업 진행, 안정화 및 확산 : 전환 후 모니터링 및 성능 평가를 통한 안정화, 추가 서비스 확장 및 연계 시스템 구축, 예시는 없이 작성해줘.",
                "필요성":f"{query}가 제대로 클라우드 서비스로 디지털 전환하기 위해서는 정부지원의 필요성을 작성해줘. 다음 내용을 참고하여 알맞게 변경해서 구체적으로 작성해줘.  1) 재정 부담 완화: 초기 클라우드 전환 시 필요한 기술 컨설팅, 시스템 구축, 보안 강화 등 고비용 투자 부담을 정부 지원을 통해 경감하고자 합니다. 2) 기술 전문성 확보: 클라우드 도입 과정에서 내부 인력만으로 해결하기 어려운 기술적 난제를 외부 전문 컨설턴트와 협업하는 등의 지원이 필요합니다. 3) 경쟁력 강화: 정부 지원을 통해 중소기업의 디지털 전환 성공 사례를 만들고, 산업 전반의 경쟁력 향상에 기여할 수 있습니다.",
                "사업계획":f"{query}가 해당 지원사업 종료 후 클라우드 서비스 도입 → 지속 활용을 통해 데이터 축척 및 기존 자사 공정데이터의 클라우드 전환 → 전사 정보의 데이터화 → 데이터 기반의 혁신기업으로 성장하기 위한 사업 계획을 알려줘. 다음 내용을 참고하여 알맞게 변경해서 구체적으로 작성해줘. 자체 운영 체제 구축: 정부 지원 기간 동안 마련한 클라우드 인프라와 노하우를 바탕으로, 자체 클라우드 운영 체계를 정비하고 지속적인 기술 업데이트를 실시합니다. 서비스 확산 및 신규 비즈니스 모델 도입:  클라우드 환경에서의 안정적 운영을 기반으로, 고객 맞춤형 서비스 개발, 데이터 분석 기반의 신규 수익 모델 도입을 추진합니다. 내부 역량 강화 및 조직 문화 전환: 클라우드 기술 활용 교육 및 전문 인력 양성을 통해, 장기적으로 IT 역량을 강화하고 디지털 전환 문화를 정착시킬 예정입니다.",
                "기대효과":f"{query}가 클라우드 서비스 도입 → 지속 활용을 통해 데이터 축척 및 기존 자사 공정데이터의 클라우드 전환 → 전사 정보의 데이터화 → 데이터 기반의 혁신기업으로 성장하기 위한 기대효과를 알려줘. 다음 내용을 참고하여 알맞게 변경해서 구체적으로 작성해줘. ",
                }
        
        json_schema = {
            "name": "keyword_response",
            "strict": True,
            "schema": {
                    "type": "object",
                    "properties": {  id: {"type": "string",   }},
                    "required": [id],
                    "additionalProperties": False
                }
            }
        model="gpt-4o-mini"
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "너는 특허와 클라우드 서비스의 전문가야. 변리사 업무에 있어 특허 클라우드 서비스의 중요성, 필요성을 잘 알고 남을 설득시킬수 있어."},
                {"role": "user", "content": f"{prompt[id]}\n예시는 다음과 같아. \n{example[id]}"}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": json_schema
            },
            temperature=0.6
        )
        return response.choices[0].message.content

    async def make_draft(self, user):
        data = {"현황":"1111",
                "이용목적":"2222",
                "이용계획":"3333",
                "필요성":"4444",
                "사업계획":"5555",
                "기대효과":"6666"}


        whois = await self.search_preview(user)

        ids = ["현황","이용목적","이용계획","필요성","사업계획", "기대효과"]

        tasks = [(whois, id) for id in ids]

        results = await asyncio.gather(*[
            self.make_content(*task)
            for task in tasks
        ])

        for result in results:
            result = json.loads(result)
            key0 = list(result.keys())[0]
            value0 = list(result.values())[0].replace("**", "").replace("####","").replace("###","").replace("##","")
            data[key0] = value0
        
        return self.make_hwp(data, user)
        # data = {}
        # for key in id:
        #     content = make_content(whois, key)
        #     content = content.replace("**", "").replcae("####","").replcae("###","").replcae("##","")
        #     content = json.loads(content)
                
        #self.make_hwp(data, user)