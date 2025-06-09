# Elasticsearch 인덱스 정보

주택청약 FAQ, 주택 정책 인덱스명
- index_name1 : embedding_apply
- index_name2 : embedding_policy

(사용 예시1)
vstore = ElasticsearchStore(
        **connection_options,  # type: ignore
        es_url=os.environ["ELASTICSEARCH_URL"],
        index_name="embedding_apply",
        embedding=embedding_model,
    )

메타데이터 정보(확정은 아니며, 메타데이터는 추가 예정)
![image](https://github.com/user-attachments/assets/e96d3ba7-4e5e-4577-84c1-d8d30c640db8)

(사용 예시2)
![image](https://github.com/user-attachments/assets/3ff3059b-97f5-458b-b6bd-685a1f77cf95)
