API = (function($) {

    var _json = {};

    function withJSON(url, callback) {
        if (_json[url] == undefined) {
            $.getJSON(url, function(json) {
                _json[url] = json;
                callback(json);
            });
        } else {
            callback(_json[url]);
        }
    }

    function withVectorFrameJSON(frame, callback) {
        withJSON(urlForFrame(frame), callback);
    }



    return {
        withJSON: withJSON,
        withVectorFrameJSON: withVectorFrameJSON
    };


    // Private functions

    function urlForFrame(frame) {
        return '/data/prefetched/step/' + frame;
    }


}(jQuery));
