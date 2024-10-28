import data_source_json.data_source_json.data_source_json

json_data_source = data_source_json.data_source_json.data_source_json.JSONDataSource('large_graph.json')
json_data_source.parse_json()
api_graph = json_data_source.convert_to_api_graph()
