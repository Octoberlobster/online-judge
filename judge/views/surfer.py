import os
from django.http import Http404, HttpResponse
from django.views import View


class SurferView(View):
    def get(self, request, filename):
        # 構建檔案路徑
        file_path = os.path.join('pages_build', filename)
        
        # 檢查檔案是否存在
        if not os.path.exists(file_path):
            raise Http404("Surfer file not found")
        
        # 檢查檔案是否在 pages_build 目錄中（安全檢查）
        if not file_path.startswith('pages_build/'):
            raise Http404("Invalid file path")
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
        except IOError:
            raise Http404("Cannot read Surfer file")
        
        # 根據檔案類型設置正確的 MIME 類型
        content_type = 'text/html'  # 預設
        if filename.endswith('.js'):
            content_type = 'application/javascript'
        elif filename.endswith('.wasm'):
            content_type = 'application/wasm'
        elif filename.endswith('.json'):
            content_type = 'application/json'
        elif filename.endswith('.css'):
            content_type = 'text/css'
        
        response = HttpResponse(content, content_type=content_type)
        
        # 設置 CORS 標頭
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response

    def options(self, request, filename):
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response 
