execute_tools state: 
State(
    messages=[
        HumanMessage(
            content='경기도 평택시 청약정보 알려주고, 관련 읍면동의 최근 거래된 아파트 평당가 알려줘', id='44f2f48e-7bd2-44c6-add7-e90ed4fb9d3d'), 
        AIMessage(
            content='', 
            additional_kwargs={
                'tool_calls': [
                    {'index': 0,
                     'id': 'call_61btGfTiBEABdOarnOGN0KvR',
                      'function': {
                        'arguments': '{"__arg1":"경기도 평택시"}',
                        'name': 'getAPTList'}, 
                        'type': 'function'}
                    ]
            }, 
            response_metadata={
                'finish_reason': 'tool_calls', 
                'model_name': 'gpt-4o-2024-08-06', 
                'system_fingerprint': 'fp_07871e2ad8'
            }, 
            id='run-5d7400ce-0b6e-414a-adc8-31466e7d3721', 
            tool_calls=[
                {'name': 'getAPTList', 
                 'args': {'__arg1': '경기도 평택시'}, 
                 'id': 'call_61btGfTiBEABdOarnOGN0KvR', 
                 'type': 'tool_call'
                }
            ]
        )
    ], 
    queries=[], 
    retrieved_docs=[], 
    apply_info={}, 
    avg_price=0.0, 
    message={}, 
    calc_avg_pyung_price_input={}, 
    result={}
)

[getAPTList] 
Tool result: 
    {'단지명': '진위역 서희스타힐스 더 파크뷰(3차)', '공급위치': '경기도 평택시 진위면 갈곶리 239-60번지 일원', '법정동코드': 41220, '공급규모': 53, '문의처': '18006366', '모집공고일': '2025-06-05', '특별공급 청약접수시작': '2025-06-16', '특별공급 청약접수종료': '2025-06-16', '1순위 해당지역 청약접수시작': '2025-06-17', '1순위 해당지역 청약접수종료': '2025-06-17', '1순위 기타지역 청약접수시작': '2025-06-17', '1순위 기타지역 청약접수 종료': '2025-06-17', '2순위 해당지역 청약접수시작': '2025-06-18', '2순위 해당지역 청약접수종료': '2025-06-18', '2순위 기타지역 청약접수시작': '2025-06-18', '2순위 기타지역 청약접수종료': '2025-06-18', '당첨자 발표일': '2025-06-24', '계약 시작': '2025-07-07', '계약 종료': '2025-07-09', '시행사': '엘지로 지역주택조합', '시공사': '(주)서희건설', '아파트 홍보 URL': 'http://www.starhills-jinwi.co.kr', '분양공고 URL': 'https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancDetail.do?houseManageNo=2025000199&pblancNo=2025000199', '평형별 공급대상 및 분양가': {'059.7537A': {'주택형': '059.7537A', '주택공급면적': '79.3049', '전체 공급세대수': '17', '특별 공급세대수': {'전체': '6', '다자녀가구': '1', '신혼부부': '3', '생애최초': '1', '청년': '0', '노부모부양': '0', '신생아(일반형)': '0', '기관추천': '1', '이전기관': '0', '기타': '0'}, '일반 공급세대수': '11', '분양가(최고가 기준)': '40,900 만원'}, '059.7718B': {'주택형': '059.7718B', '주택공급면적': '79.1417', '전체 공급세대수': '6', '특별 공급세대수': {'전체': '5', '다자녀가구': '1', '신혼부부': '2', '생애최초': '1', '청년': '0', '노부모부양': '0', '신생아(일반형)': '0', '기관추천': '1', '이전기관': '0', '기타': '0'}, '일반 공급세대수': '1', '분양가(최고가 기준)': '38,800 만원'}, '071.7007B': {'주택형': '071.7007B', '주택공급면적': '93.8458', '전체 공급세대수': '13', '특별 공급세대수': {'전체': '7', '다자녀가구': '1', '신혼부부': '3', '생애최초': '1', '청년': '0', '노부모부양': '1', '신생아(일반형)': '0', '기관추천': '1', '이전기관': '0', '기타': '0'}, '일반 공급 세대수': '6', '분양가(최고가 기준)': '48,400 만원'}, '071.4998D': {'주택형': '071.4998D', '주택공급면적': '94.6473', '전체 공급세대수': '9', '특별 공급세대수': {'전체': '5', '다자녀가구': '1', '신혼부부': '2', '생애최초': '1', '청년': '0', '노부모부양': '0', '신생아(일반형)': '0', '기관추천': '1', '이전기관': '0', '기타': '0'}, '일반 공급세대수': '4', '분양가(최고가 기준)': '47,800 만원'}, '084.8277A': {'주택형': '084.8277A', '주택공급면적': '110.3695', '전체 공급세대수': '7', '특별 공급세대수': {'전체': '3', '다자녀가구': '1', '신혼부부': '1', '생애최초': '0', '청년': '0', '노부모부양': '0', '신생아(일반형)': '0', '기관추천': '1', '이전기관': '0', '기타': '0'}, '일반 공급세대수': '4', '분양가(최고가 기준)': '54,600 만원'}, '084.7233B': {'주택형': '084.7233B', '주택공급면적': '110.2712', '전체 공급세대수': '1', '특별 공급세대수': {'전체': '0', '다자녀가구': '0', '신혼부부': '0', '생애최초': '0', '청년': '0', '노부모부양': '0', '신생아(일반형)': '0', '기관추천': '0', '이전기관': '0', '기타': '0'}, '일반 공급세대수': '1', '분양가(최고가 기준)': '54,500 만원'}}}

execute_tools state: 
State(
    messages=[
        HumanMessage(
            content='경기도 평택시 청약정보 알려주고, 관련 읍면동의 최근 거래된 아파트 평당가 알려줘', id='44f2f48e-7bd2-44c6-add7-e90ed4fb9d3d'), 
        AIMessage(
            content='', additional_kwargs={'tool_calls': [{'index': 0, 'id': 'call_61btGfTiBEABdOarnOGN0KvR', 'function': {'arguments': '{"__arg1":"경기도 평택시"}', 'name': 'getAPTList'}, 'type': 'function'}]}, response_metadata={'finish_reason': 'tool_calls', 'model_name': 'gpt-4o-2024-08-06', 'system_fingerprint': 'fp_07871e2ad8'}, id='run-5d7400ce-0b6e-414a-adc8-31466e7d3721', tool_calls=[{'name': 'getAPTList', 'args': {'__arg1': '경기도 평택시'}, 'id': 'call_61btGfTiBEABdOarnOGN0KvR', 'type': 'tool_call'}]), ToolMessage(content='{"\\ub2e8\\uc9c0\\uba85": "\\uc9c4\\uc704\\uc5ed \\uc11c\\ud76c\\uc2a4\\ud0c0\\ud790\\uc2a4 \\ub354 \\ud30c\\ud06c\\ubdf0(3\\ucc28)", "\\uacf5\\uae09\\uc704\\uce58": "\\uacbd\\uae30\\ub3c4 \\ud3c9\\ud0dd\\uc2dc \\uc9c4\\uc704\\uba74 \\uac08\\uacf6\\ub9ac 239-60\\ubc88\\uc9c0 \\uc77c\\uc6d0", "\\ubc95\\uc815\\ub3d9\\ucf54\\ub4dc": 41220, "\\uacf5\\uae09\\uaddc\\ubaa8": 53, "\\ubb38\\uc758\\ucc98": "18006366", "\\ubaa8\\uc9d1\\uacf5\\uace0\\uc77c": "2025-06-05", "\\ud2b9\\ubcc4\\uacf5\\uae09 \\uccad\\uc57d\\uc811\\uc218\\uc2dc\\uc791": "2025-06-16", "\\ud2b9\\ubcc4\\uacf5\\uae09 \\uccad\\uc57d\\uc811\\uc218\\uc885\\ub8cc": "2025-06-16", "1\\uc21c\\uc704 \\ud574\\ub2f9\\uc9c0\\uc5ed \\uccad\\uc57d\\uc811\\uc218\\uc2dc\\uc791": "2025-06-17", "1\\uc21c\\uc704 \\ud574\\ub2f9\\uc9c0\\uc5ed \\uccad\\uc57d\\uc811\\uc218\\uc885\\ub8cc": "2025-06-17", "1\\uc21c\\uc704 \\uae30\\ud0c0\\uc9c0\\uc5ed \\uccad\\uc57d\\uc811\\uc218\\uc2dc\\uc791": "2025-06-17", "1\\uc21c\\uc704 \\uae30\\ud0c0\\uc9c0\\uc5ed \\uccad\\uc57d\\uc811\\uc218\\uc885\\ub8cc": "2025-06-17", "2\\uc21c\\uc704 \\ud574\\ub2f9\\uc9c0\\uc5ed \\uccad\\uc57d\\uc811\\uc218\\uc2dc\\uc791": "2025-06-18", "2\\uc21c\\uc704 \\ud574\\ub2f9\\uc9c0\\uc5ed \\uccad\\uc57d\\uc811\\uc218\\uc885\\ub8cc": "2025-06-18", "2\\uc21c\\uc704 \\uae30\\ud0c0\\uc9c0\\uc5ed \\uccad\\uc57d\\uc811\\uc218\\uc2dc\\uc791": "2025-06-18", "2\\uc21c\\uc704 \\uae30\\ud0c0\\uc9c0\\uc5ed \\uccad\\uc57d\\uc811\\uc218\\uc885\\ub8cc": "2025-06-18", "\\ub2f9\\ucca8\\uc790 \\ubc1c\\ud45c\\uc77c": "2025-06-24", "\\uacc4\\uc57d \\uc2dc\\uc791": "2025-07-07", "\\uacc4\\uc57d \\uc885\\ub8cc": "2025-07-09", "\\uc2dc\\ud589\\uc0ac": "\\uc5d8\\uc9c0\\ub85c \\uc9c0\\uc5ed\\uc8fc\\ud0dd\\uc870\\ud569", "\\uc2dc\\uacf5\\uc0ac": "(\\uc8fc)\\uc11c\\ud76c\\uac74\\uc124", "\\uc544\\ud30c\\ud2b8 \\ud64d\\ubcf4 URL": "http://www.starhills-jinwi.co.kr", "\\ubd84\\uc591\\uacf5\\uace0 URL": "https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancDetail.do?houseManageNo=2025000199&pblancNo=2025000199", "\\ud3c9\\ud615\\ubcc4 \\uacf5\\uae09\\ub300\\uc0c1 \\ubc0f \\ubd84\\uc591\\uac00": {"059.7537A": {"\\uc8fc\\ud0dd\\ud615": "059.7537A", "\\uc8fc\\ud0dd\\uacf5\\uae09\\uba74\\uc801": "79.3049", "\\uc804\\uccb4 \\uacf5\\uae09\\uc138\\ub300\\uc218": "17", "\\ud2b9\\ubcc4 \\uacf5\\uae09\\uc138\\ub300\\uc218": {"\\uc804\\uccb4": "6", "\\ub2e4\\uc790\\ub140\\uac00\\uad6c": "1", "\\uc2e0\\ud63c\\ubd80\\ubd80": "3", "\\uc0dd\\uc560\\ucd5c\\ucd08": "1", "\\uccad\\ub144": "0", "\\ub178\\ubd80\\ubaa8\\ubd80\\uc591": "0", "\\uc2e0\\uc0dd\\uc544(\\uc77c\\ubc18\\ud615)": "0", "\\uae30\\uad00\\ucd94\\ucc9c": "1", "\\uc774\\uc804\\uae30\\uad00": "0", "\\uae30\\ud0c0": "0"}, "\\uc77c\\ubc18 \\uacf5\\uae09\\uc138\\ub300\\uc218": "11", "\\ubd84\\uc591\\uac00(\\ucd5c\\uace0\\uac00 \\uae30\\uc900)": "40,900 \\ub9cc\\uc6d0"}, "059.7718B": {"\\uc8fc\\ud0dd\\ud615": "059.7718B", "\\uc8fc\\ud0dd\\uacf5\\uae09\\uba74\\uc801": "79.1417", "\\uc804\\uccb4 \\uacf5\\uae09\\uc138\\ub300\\uc218": "6", "\\ud2b9\\ubcc4 \\uacf5\\uae09\\uc138\\ub300\\uc218": {"\\uc804\\uccb4": "5", "\\ub2e4\\uc790\\ub140\\uac00\\uad6c": "1", "\\uc2e0\\ud63c\\ubd80\\ubd80": "2", "\\uc0dd\\uc560\\ucd5c\\ucd08": "1", "\\uccad\\ub144": "0", "\\ub178\\ubd80\\ubaa8\\ubd80\\uc591": "0", "\\uc2e0\\uc0dd\\uc544(\\uc77c\\ubc18\\ud615)": "0", "\\uae30\\uad00\\ucd94\\ucc9c": "1", "\\uc774\\uc804\\uae30\\uad00": "0", "\\uae30\\ud0c0": "0"}, "\\uc77c\\ubc18 \\uacf5\\uae09\\uc138\\ub300\\uc218": "1", "\\ubd84\\uc591\\uac00(\\ucd5c\\uace0\\uac00 \\uae30\\uc900)": "38,800 \\ub9cc\\uc6d0"}, "071.7007B": {"\\uc8fc\\ud0dd\\ud615": "071.7007B", "\\uc8fc\\ud0dd\\uacf5\\uae09\\uba74\\uc801": "93.8458", "\\uc804\\uccb4 \\uacf5\\uae09\\uc138\\ub300\\uc218": "13", "\\ud2b9\\ubcc4 \\uacf5\\uae09\\uc138\\ub300\\uc218": {"\\uc804\\uccb4": "7", "\\ub2e4\\uc790\\ub140\\uac00\\uad6c": "1", "\\uc2e0\\ud63c\\ubd80\\ubd80": "3", "\\uc0dd\\uc560\\ucd5c\\ucd08": "1", "\\uccad\\ub144": "0", "\\ub178\\ubd80\\ubaa8\\ubd80\\uc591": "1", "\\uc2e0\\uc0dd\\uc544(\\uc77c\\ubc18\\ud615)": "0", "\\uae30\\uad00\\ucd94\\ucc9c": "1", "\\uc774\\uc804\\uae30\\uad00": "0", "\\uae30\\ud0c0": "0"}, "\\uc77c\\ubc18 \\uacf5\\uae09\\uc138\\ub300\\uc218": "6", "\\ubd84\\uc591\\uac00(\\ucd5c\\uace0\\uac00 \\uae30\\uc900)": "48,400 \\ub9cc\\uc6d0"}, "071.4998D": {"\\uc8fc\\ud0dd\\ud615": "071.4998D", "\\uc8fc\\ud0dd\\uacf5\\uae09\\uba74\\uc801": "94.6473", "\\uc804\\uccb4 \\uacf5\\uae09\\uc138\\ub300\\uc218": "9", "\\ud2b9\\ubcc4 \\uacf5\\uae09\\uc138\\ub300\\uc218": {"\\uc804\\uccb4": "5", "\\ub2e4\\uc790\\ub140\\uac00\\uad6c": "1", "\\uc2e0\\ud63c\\ubd80\\ubd80": "2", "\\uc0dd\\uc560\\ucd5c\\ucd08": "1", "\\uccad\\ub144": "0", "\\ub178\\ubd80\\ubaa8\\ubd80\\uc591": "0", "\\uc2e0\\uc0dd\\uc544(\\uc77c\\ubc18\\ud615)": "0", "\\uae30\\uad00\\ucd94\\ucc9c": "1", "\\uc774\\uc804\\uae30\\uad00": "0", "\\uae30\\ud0c0": "0"}, "\\uc77c\\ubc18 \\uacf5\\uae09\\uc138\\ub300\\uc218": "4", "\\ubd84\\uc591\\uac00(\\ucd5c\\uace0\\uac00 \\uae30\\uc900)": "47,800 \\ub9cc\\uc6d0"}, "084.8277A": {"\\uc8fc\\ud0dd\\ud615": "084.8277A", "\\uc8fc\\ud0dd\\uacf5\\uae09\\uba74\\uc801": "110.3695", "\\uc804\\uccb4 \\uacf5\\uae09\\uc138\\ub300\\uc218": "7", "\\ud2b9\\ubcc4 \\uacf5\\uae09\\uc138\\ub300\\uc218": {"\\uc804\\uccb4": "3", "\\ub2e4\\uc790\\ub140\\uac00\\uad6c": "1", "\\uc2e0\\ud63c\\ubd80\\ubd80": "1", "\\uc0dd\\uc560\\ucd5c\\ucd08": "0", "\\uccad\\ub144": "0", "\\ub178\\ubd80\\ubaa8\\ubd80\\uc591": "0", "\\uc2e0\\uc0dd\\uc544(\\uc77c\\ubc18\\ud615)": "0", "\\uae30\\uad00\\ucd94\\ucc9c": "1", "\\uc774\\uc804\\uae30\\uad00": "0", "\\uae30\\ud0c0": "0"}, "\\uc77c\\ubc18 \\uacf5\\uae09\\uc138\\ub300\\uc218": "4", "\\ubd84\\uc591\\uac00(\\ucd5c\\uace0\\uac00 \\uae30\\uc900)": "54,600 \\ub9cc\\uc6d0"}, "084.7233B": {"\\uc8fc\\ud0dd\\ud615": "084.7233B", "\\uc8fc\\ud0dd\\uacf5\\uae09\\uba74\\uc801": "110.2712", "\\uc804\\uccb4 \\uacf5\\uae09\\uc138\\ub300\\uc218": "1", "\\ud2b9\\ubcc4 \\uacf5\\uae09\\uc138\\ub300\\uc218": {"\\uc804\\uccb4": "0", "\\ub2e4\\uc790\\ub140\\uac00\\uad6c": "0", "\\uc2e0\\ud63c\\ubd80\\ubd80": "0", "\\uc0dd\\uc560\\ucd5c\\ucd08": "0", "\\uccad\\ub144": "0", "\\ub178\\ubd80\\ubaa8\\ubd80\\uc591": "0", "\\uc2e0\\uc0dd\\uc544(\\uc77c\\ubc18\\ud615)": "0", "\\uae30\\uad00\\ucd94\\ucc9c": "0", "\\uc774\\uc804\\uae30\\uad00": "0", "\\uae30\\ud0c0": "0"}, "\\uc77c\\ubc18 \\uacf5\\uae09\\uc138\\ub300\\uc218": "1", "\\ubd84\\uc591\\uac00(\\ucd5c\\uace0\\uac00 \\uae30\\uc900)": "54,500 \\ub9cc\\uc6d0"}}}', name='getAPTList', id='a75e8439-8905-4ee3-855b-0e716c79fbeb', tool_call_id='call_61btGfTiBEABdOarnOGN0KvR'), 
        AIMessage(content='', additional_kwargs={'tool_calls': [{'index': 0, 'id': 'call_iZQDuboJi74mlGeSvmEloRCh', 'function': {'arguments': '{"__arg1":"경기도 평택시"}', 'name': 'calc_avg_pyung_price'}, 'type': 'function'}]}, response_metadata={'finish_reason': 'tool_calls', 'model_name': 'gpt-4o-2024-08-06', 'system_fingerprint': 'fp_07871e2ad8'}, id='run-fb964c21-9562-4660-bbd0-0ef330009360', tool_calls=[{'name': 'calc_avg_pyung_price', 'args': {'__arg1': '경기도 평택시'}, 'id': 'call_iZQDuboJi74mlGeSvmEloRCh', 'type': 'tool_call'}])
    ], 
    queries=[], 
    retrieved_docs=[], 
    apply_info={}, 
    avg_price=0.0, 
    message={}, 
    calc_avg_pyung_price_input={}, 
    result={}
)