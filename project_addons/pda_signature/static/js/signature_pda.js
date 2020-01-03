odoo.define('pda_signature.signature_pda', function (require) {
    "use strict";

    var rpc = require('web.rpc');
    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    $(document).on('click', 'button.pda_call', function (event) {
        event.preventDefault();
        console.log("Iniciando PDA");

        var type = window.location.hash.substr(1);

        var result = type.split('&').reduce(function (result, item) {
            var parts = item.split('=');
            result[parts[0]] = parts[1];
            return result;
        }, {});

        console.log(result);


        var id = result['id'];
        var model = result['model'];
        console.log("Estamos en el batch picking nº: " + id);


        var domain = ['id', '=', id];
        var fields = ["signature_firstName", "signature_lastName", "signature_email", "signature_location"];
        var imgWidth = 300;
        var imgHeight = 150;

        rpc.query({
            model: model,
            method: 'search_read',
            domain: [domain],
            fields: fields
        })
        .then(function(data){
            var message  =  {                  
                "firstName": data[0]['signature_firstName'],  
                "lastName": data[0]['signature_lastName'],  
                "eMail": data[0]['signature_email'],  
                "location": data[0]['signature_location'], 
                "imageFormat": 1,  
                "imageX": imgWidth,  
                "imageY": imgHeight,  
                "imageTransparency": false,  
                "imageScaling": false,  
                "maxUpScalePercent": 0.0,  
                "rawDataFormat": "ENC", 
                "minSigPoints": 2
            };

            console.log(message);

            document.addEventListener('SigCaptureWeb_SignResponse', SignResponse, false);
            var messageData = JSON.stringify(message);
            var element = document.createElement('SignCaptureWeb_ExtnDataElem');
            element.setAttribute('SigCaptureWeb_MsgAttribute', messageData);
            document.documentElement.appendChild(element);
            var evt = document.createEvent("Events");
            evt.initEvent('SigCaptureWeb_SignStartEvent', true, false);
            element.dispatchEvent(evt);
            function SignResponse(event) {
                var str = event.target.getAttribute("SigCaptureWeb_msgAttri");
                var obj = JSON.parse(str);
                console.log(obj);

                var signature_data = {
                    signature_firstName: data[0]['signature_firstName'],
                    signature_lastName: data[0]['signature_lastName'],
                    signature_email: data[0]['signature_email'],
                    signature_location: data[0]['signature_location'],
                    signature_error: obj['errorMsg'],
                    signature_image_data: obj['imageData'],
                    signature_is_signed: obj['isSigned'],
                    signature_pad_info: obj['padInfo'],
                    signature_raw_data: obj['rawData'],
                    signature_sig_string: obj['sigString']
                }
                
                console.log(obj['errorMsg']);
                rpc.query({
                    model: 'stock.batch.picking',
                    method: 'save_pda_data',
                    args: [id, signature_data],
                })
                .then(function () {
                    console.log("Datos guardados");
                })
                
            } 
        });
    });

});