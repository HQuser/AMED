var labelType, useGradients, nativeTextSupport, animate;

(function () {
    var ua = navigator.userAgent,
        iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
        typeOfCanvas = typeof HTMLCanvasElement,
        nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
        textSupport = nativeCanvasSupport
            && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
    //I'm setting this based on the fact that ExCanvas provides text support for IE
    //and that as of today iPhone/iPad current text support is lame
    labelType = (!nativeCanvasSupport || (textSupport && !iStuff)) ? 'Native' : 'HTML';
    nativeTextSupport = labelType == 'Native';
    useGradients = nativeCanvasSupport;
    animate = !(iStuff || !nativeCanvasSupport);
})();

var Log = {
    elem: false,
    write: function (text) {
        if (!this.elem)
            this.elem = document.getElementById('log');
        this.elem.innerHTML = text;
        this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
    }
};

var json_history = [];

$.ajax({
    url: 'http://127.0.0.1:8000/get_clusters',
    type: 'GET',
    async: false,
    cache: false,
    timeout: 30000,
    fail: function () {
        return true;
    },
    success: function (msg) {
        json_history.push(msg.data);
        console.log(msg)
    }
});


function backtrack() {
    // json_history.push(data.data);
    if (index !== 0) index -= 1;
    else return;
    // console.log("backgrack clicked");
    rgraph.loadJSON(json_history[index]);
    rgraph.compute('end');
    rgraph.refresh();

    setTimeout(function () {
        simulate(document.getElementById("btn"), "click", {
            pointerX: Screen.PrimaryScreen.Bounds.Width / 2,
            pointerY: Screen.PrimaryScreen.Bounds.Height / 2 - 100
        })
    }, 2000);
}

var rgraph = 0;

var index = 0;

function init() {
    //init data
    var json = json_history[index];
    console.log(json);

    //init RGraph
    rgraph = new $jit.RGraph({
        // Adding on click
        Events: {
            enable: true,
            onClick: function (node, eventInfo, e) {
            }
        },
        //Where to append the visualization
        injectInto: 'infovis',
        //Optional: create a background canvas that plots
        //concentric circles.
        background: {
            CanvasStyles: {
                strokeStyle: '#555'
            }
        },
        //Add navigation capabilities:
        //zooming by scrolling and panning.
        Navigation: {
            enable: true,
            panning: true,
            zooming: 70
        },
        //Set Node and Edge styles.
        Node: {
            color: '#ddeeff'
        },

        Edge: {
            color: '#C17878',
            lineWidth: 0.25,
            alpha: 0.7
            // overridable: true,
            // type: 'label-arrow-line'
        },

        onBeforeCompute: function (node) {
            Log.write("centering " + node.name + "...");
            console.log(node);
            // id = node.id;
            if (node.id.endsWith('c')) {
                $.get("http://127.0.0.1:8000/get_clust_data?id=" + node.id, function (data, status) {
                    // alert("Data: " + data + "\nStatus: " + status);
                    console.log(data.data);
                    json_history.push(data.data);
                    index += 1;

                    console.log(json_history);
                    console.log(index);

                    //load JSON data
                    rgraph.loadJSON(data.data);
                    rgraph.compute('end');
                    // reload_graph();

                    rgraph.refresh();
                });
            }
            //Add the relation list in the right column.
            //This list is taken from the data property of each JSON node.
            console.log("Band Data");
            console.log(node.data.band);
            $jit.id('inner-details').innerHTML = node.data.band;
        },

        //Add the name of the node in the correponding label
        //and a click handler to move the graph.
        //This method is called once, on label creation.
        onCreateLabel: function (domElement, node) {

            var id = domElement.attributes.id.value;

            // console.log(domElement);
            domElement.innerHTML = node.name;
            var style = domElement.style;
            style.fontSize = "0.5em";
            style.color = "#fff";
            style.cursor = "pointer";
            // console.log(node);
            domElement.childNodes[0]['data'] = domElement.childNodes[0]['data'].substring(0, 20) + "...";
            if (id.endsWith('c')) {
                // style.fontSize = "1.5em";
                //Text colour of ring 1 nodes
                style.color = "#ffffff";
                style.backgroundColor = "#FD7E14";
                // style.padding = "1px 3px";

            } else if (id.endsWith('d')) {
                // style.fontSize = "0.8em";
                //Text colour of ring 1 nodes
                style.color = "#FFFFFF";
                style.backgroundColor = "#F783AC";
                // console.log(domElement.childNodes[0]['data']);
                // style.padding = "1px 3px";

            } else {
                // style.fontSize = "0.7em";
                //Text colour of ring 2 nodes
                if (id.endsWith('q')) {
                    style.color = "#000000";
                    style.backgroundColor = "#ffffff";
                } else {
                    style.color = "#ffffff";
                    style.backgroundColor = "#83ACF7";
                }
            }

            domElement.onclick = function () {
                rgraph.onClick(node.id, {
                    onComplete: function () {
                        Log.write("done");
                    }
                });
            };
        },
        //Change some label dom properties.
        //This method is called each time a label is plotted.
        onPlaceLabel: function (domElement, node) {
            var style = domElement.style;
            style.display = '';
            style.cursor = 'pointer';

            if (node._depth <= 1) {
                style.fontSize = "0.8em";
                style.color = "#494949";

            } else if (node._depth == 2) {
                style.fontSize = "0.8em";
                style.color = "#494949";

            } else {
                style.fontSize = "0.7em";
                style.display = 'none';
            }

            node.Edge.color = "#FFFFFF";
            var left = parseInt(style.left);
            var w = domElement.offsetWidth;
            style.left = (left - w / 2) + 'px';
        }
    });
    //load JSON data
    rgraph.loadJSON(json);
    //trigger small animation
    rgraph.graph.eachNode(function (n) {
        var pos = n.getPos();
        pos.setc(-200, -200);
    });
    rgraph.compute('end');
    rgraph.fx.animate({
        modes: ['polar'],
        duration: 1000
    });
    //end
    //append information about the root relations in the right column
    $jit.id('inner-details').innerHTML = rgraph.graph.getNode(rgraph.root).data.relation;
}

function reload_graph() {
    init();
    return 0;
}


function simulate(element, eventName) {
    var options = extend(defaultOptions, arguments[2] || {});
    var oEvent, eventType = null;

    for (var name in eventMatchers) {
        if (eventMatchers[name].test(eventName)) {
            eventType = name;
            break;
        }
    }

    if (!eventType)
        throw new SyntaxError('Only HTMLEvents and MouseEvents interfaces are supported');

    if (document.createEvent) {
        oEvent = document.createEvent(eventType);
        if (eventType == 'HTMLEvents') {
            oEvent.initEvent(eventName, options.bubbles, options.cancelable);
        } else {
            oEvent.initMouseEvent(eventName, options.bubbles, options.cancelable, document.defaultView,
                options.button, options.pointerX, options.pointerY, options.pointerX, options.pointerY,
                options.ctrlKey, options.altKey, options.shiftKey, options.metaKey, options.button, element);
        }
        element.dispatchEvent(oEvent);
    } else {
        options.clientX = options.pointerX;
        options.clientY = options.pointerY;
        var evt = document.createEventObject();
        oEvent = extend(evt, options);
        element.fireEvent('on' + eventName, oEvent);
    }
    return element;
}

function extend(destination, source) {
    for (var property in source)
        destination[property] = source[property];
    return destination;
}

var eventMatchers = {
    'HTMLEvents': /^(?:load|unload|abort|error|select|change|submit|reset|focus|blur|resize|scroll)$/,
    'MouseEvents': /^(?:click|dblclick|mouse(?:down|up|over|move|out))$/
}
var defaultOptions = {
    pointerX: 0,
    pointerY: 0,
    button: 0,
    ctrlKey: false,
    altKey: false,
    shiftKey: false,
    metaKey: false,
    bubbles: true,
    cancelable: true
}