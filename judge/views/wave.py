import os
from django.http import Http404, HttpResponse
from django.views import View


class WaveformView(View):
    def get(self, request, filename):
        # 檢查檔案是否存在
        file_path = os.path.join('waves', filename)
        if not os.path.exists(file_path):
            raise Http404("VCD file not found")
        
        # 檢查檔案副檔名
        if not filename.endswith('.vcd'):
            raise Http404("Invalid file type")
        
        # 讀取檔案內容
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
        except IOError:
            raise Http404("Cannot read VCD file")
        
                # 返回檔案內容
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Add CORS headers to allow cross-origin requests
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
    
    def options(self, request, filename):
        # Handle preflight OPTIONS requests
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response 
