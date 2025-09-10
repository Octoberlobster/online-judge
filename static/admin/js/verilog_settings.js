(function() {
    'use strict';
    
    function toggleVerilogFields() {
        var enablePPACheckbox = document.getElementById('id_enable_ppa');
        if (!enablePPACheckbox) return;
        
        var enablePPA = enablePPACheckbox.checked;
        
        var verilogFieldIds = [
            'id_f4pga_board',
            'id_f4pga_target_fmax',
            'id_openlane_pdk',
            'id_openlane_ppa_score',
            'id_openlane_critical_path_ns',
            'id_openlane_core_area_um2',
            'id_openlane_power_total'
        ];
        
        verilogFieldIds.forEach(function(fieldId) {
            var field = document.getElementById(fieldId);
            if (!field) return;
            
            // 找到包含這個欄位的行
            var fieldRow = field.closest('.field-row') || field.closest('.form-row');
            if (!fieldRow) {
                // 如果找不到 .field-row 或 .form-row，試試找父元素
                fieldRow = field.parentElement;
                while (fieldRow && !fieldRow.classList.contains('field-row') && !fieldRow.classList.contains('form-row')) {
                    fieldRow = fieldRow.parentElement;
                }
            }
            
            if (fieldRow) {
                if (enablePPA) {
                    fieldRow.style.display = '';
                } else {
                    fieldRow.style.display = 'none';
                    field.value = '';  // 清空欄位值
                }
            }
        });
    }
    
    function initVerilogSettings() {
        var enablePPACheckbox = document.getElementById('id_enable_ppa');
        if (enablePPACheckbox) {
            // 初始化時執行一次
            toggleVerilogFields();
            
            // 當 checkbox 改變時執行
            enablePPACheckbox.addEventListener('change', toggleVerilogFields);
        }
    }
    
    // 等待 DOM 載入完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVerilogSettings);
    } else {
        initVerilogSettings();
    }
    
})();
