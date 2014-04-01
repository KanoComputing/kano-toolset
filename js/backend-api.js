// backend-api.js
//
// Copyright (C) 2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//

window.backend = {
    callbacks: [],

    call: function() {
        if (arguments.length >= 1) {
            func = arguments[0];
            args = [];

            if (arguments.length > 1 &&
                typeof arguments[arguments.length - 1] === 'function') {

                arguments = Array.prototype.slice.call(arguments, 0);
                callback = arguments.pop();
                timestamp = (new Date).getTime();

                this.callbacks.push({
                    timestamp: timestamp,
                    func: func,
                    callback: callback
                });
                func += '[' + timestamp + ']';
            }

            for (var i = 1; i < arguments.length; i += 1) {
                args.push(encodeURIComponent(arguments[i].toString()));
            }

        } else {
            func = 'error';
            args = [encodeURIComponent('Invalid API call - no arguments passed.')];
        }

        var args_string = args.join('/');

        window.location.hash = 'api:' + func + '/' + args_string;
    },

    trigger_cb: function(cb_name, timestamp, result) {
        if (typeof result === 'string') {
            result = decodeURIComponent(result);
        }

        for (var i = 0; i < backend.callbacks.length; i += 1) {
            callback = backend.callbacks[i];
            if (callback.func === cb_name &&
                callback.timestamp === timestamp) {
                callback.callback(result);
                backend.callbacks.splice(i, 1);
                break;
            }
        }

    }
};
