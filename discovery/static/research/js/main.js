function dispatch_request(parameters) {
    console.log(parameters);
    if (!does_param_exists('ft_search') && !parameters.includes("ft_search")) {
        if ($("#ftsearch").val().trim() != "")
            parameters = parameters + '&ft_search=' + $("#ftsearch").val(); // TODO Ask for better flow for this e.g. FT first or allow FT along with filters at the same time

        if (!does_param_exists('lookup') && !parameters.includes("lookup")) {
            parameters = parameters + '&lookup=clust';
        }
    }
    window.location.replace(window.location.origin + "/?" + parameters);
}

$("#implicitFTS").on('click keydown', (e) => {
    if (e.keyCode && e.keyCode == 13 || e.type == "click") {
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);

        let lookup = urlParams.get('lookup');

        params = ""

        if (lookup !== "") params = "lookup=" + lookup;
        else params = "lookup=clust";

        dispatch_request(params + "&ft_search=" + val);
    }
});

function get_url_parameters() {
    return location.search.replace("?", "");
}

function does_param_exists(value) {
    var regex = value;
    var parms = get_url_parameters();

    return parms.search(regex) >= 0;
}

$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    }
    return decodeURI(results[1]) || 0;
}

function get_array_url_params() {
    var get = [];
    arr = location.search.replace('?', '').split('&');
    for (var i = 0, len = arr.length; i < len; i++) {
        split = arr[i].split("=", 2);
        get[split[0]] = split[1];
    }

    return get;
}

$(document).on('click', 'a', function (e) {
    e.preventDefault();
    var url = $(this).attr('href');
    window.open(url, '_blank');
});

/* ===== Logic for creating fake Select Boxes ===== */
$('.sel').each(function () {
    $(this).children('select').css('display', 'none');

    var $current = $(this);

    $(this).find('option').each(function (i) {
        if (i == 0) {
            $current.prepend($('<div>', {
                class: $current.attr('class').replace(/sel/g, 'sel__box')
            }));

            var placeholder = $.urlParam('engine') === null ? $(this).text() : $.urlParam('engine');

            console.log(placeholder);
            $current.prepend($('<span>', {
                class: $current.attr('class').replace(/sel/g, 'sel__placeholder'),
                text: placeholder,
                'data-placeholder': placeholder
            }));

            if ($.urlParam('engine') !== null) {
                $(".sel__placeholder").css('color', 'white');
            }
            return;
        }

        $current.children('div').append($('<span>', {
            class: $current.attr('class').replace(/sel/g, 'sel__box__options'),
            text: $(this).text()
        }));
    });
});

// Toggling the `.active` state on the `.sel`.
$('.sel').click(function () {
    $(this).toggleClass('active');
});

// Toggling the `.selected` state on the options.
$('.sel__box__options').click(function () {
    var txt = $(this).text();
    var index = $(this).index();

    $(this).siblings('.sel__box__options').removeClass('selected');
    $(this).addClass('selected');

    var $currentSel = $(this).closest('.sel');
    $currentSel.children('.sel__placeholder').text(txt);
    $currentSel.children('select').prop('selectedIndex', index + 1);
});

// Collapsable Div
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function () {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
            content.style.display = "none";
        } else {
            content.style.display = "block";
        }
    });
}

// Toggler Nav
$(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar, #content').toggleClass('active');
    });
});

// DATE RANGE
$(function () {

    var startDate = null;
    var endDate = null;

    if ($.urlParam('start_date') !== null) {
        startDate = $.urlParam('sdate');
        endDate = $.urlParam('edate');
    }

    var start_date = startDate === null ? moment().subtract(29, 'days') : moment(new Date(startDate));
    var end_date = endDate === null ? moment() : moment(new Date(endDate));

    function cb(start, end) {

        sdate = start.format('MM/DD/YYYY');
        edate = end.format('MM/DD/YYYY');
        console.log(start + '...' + end);

        // If date already in parameter then set detfault date to it
        if ($.urlParam('sdate') !== null) { // Not forced to change the date aka initial
            console.log(sdate + "here");
            // $('#reportrange span').html(sdate + ' - ' + edate);
            if ($.urlParam('sdate') !== sdate || $.urlParam('edate') !== edate) {
                sregex = /(sdate=)\d{2}\/\d{2}\/\d{4}/
                eregex = /(edate=)\d{2}\/\d{2}\/\d{4}/

                dispatch_request(get_url_parameters()
                    .replace(sregex, 'sdate=' + sdate)
                    .replace(eregex, 'edate=' + edate));
            } else {
                sdate = $.urlParam('sdate');
                edate = $.urlParam('edate');

                $('#reportrange span').html(sdate + ' - ' + edate);
            }
        } else if ($.urlParam('sdate') === null) {
            if (prevent_filter_before_search()) {
                return;
            } else {
                dispatch_request(get_url_parameters() + '&sdate=' + sdate + '&edate=' + edate);
            }
        } else {
            $('#reportrange span').html('Click to choose date');
        }

        console.log(start.format('MM/DD/YYYY'));
    }

    $('#reportrange').daterangepicker({
        autoUpdateInput: false,
        startDate: start_date,
        endDate: end_date,
        ranges: {
            'Today': [moment(), moment()],
            'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Last 7 Days': [moment().subtract(6, 'days'), moment()],
            'Last 30 Days': [moment().subtract(29, 'days'), moment()],
            'This Month': [moment().startOf('month'), moment().endOf('month')],
            'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    }, cb);

    // If date already in parameter then set detfault date to it
    if ($.urlParam('sdate') !== null) { // Not forced to change the date aka initial
        sdate = $.urlParam('sdate');
        edate = $.urlParam('edate');

        $('#reportrange span').html(sdate + ' - ' + edate);
    } else {
        $('#reportrange span').html('Click to choose date');
    }

    // cb(start_date, end_date);
});

$('body').on('DOMSubtreeModified', '.sel__placeholder', function () {
        var text = $(".sel__placeholder").text();

        console.log(text);
        if (text !== "Change Search Engine"
            && (text === 'Google'
                || text === 'Yahoo!'
                || text === 'Yandex'
                || text === 'Qwant'
                || text === 'Bing')) {

            $(".sel__placeholder").css('color', 'white');

            var get = get_array_url_params();

            if ('engine' in get) {
                if (get['engine'] !== text) {
                    console.log(get['engine'] + "in URL " + text);
                    console.log(!text.trim());

                    var regex = /(engine=\w)\w+/;
                    dispatch_request(get_url_parameters().replace(regex, "engine=" + text));
                }
            } else {
                if (prevent_filter_before_search()) {
                    return;
                } else {
                    dispatch_request(get_url_parameters() + "&engine=" + text);
                }
            }
        }
    }
)

function fetch_doc() {
    console.log($(this).attr('id'))

    var offset = $(this).offset();

    $.get("/get_doc?doc_id=" + $(this).attr('id'), function (data) {
        // Display the returned data in browser
        $('.doc-preview-pane').empty();
        $('.doc-preview-pane').html(data);

        // Move it to relative to the current div
        if ($(window).scrollTop() !== 0) {
            $('.doc-preview-pane').offset({top: offset.top}).css('height', 'fit-content');
            console.log(data)
        } else {
            $('.doc-preview-pane').offset({top: 110}).css('height', 'fit-content');
        }
    });
}

$('.doc-title').click(function () {
    fetch_doc.call(this);
});
$('.doc-title-overview').click(function () {
    fetch_doc.call(this);
});

$(document).on("click", "#close-preview-doc", function () {

    console.log("here");
    $('.doc-preview-pane').empty();
});

function jump(id) {
    $('html, body').animate({
        scrollTop: $("#" + id).offset().top
    }, 2000);

    console.log(id);
}

// $.dynaCloud.max = 10;
// $.merge($.dynacloud.stopwords, [ 'Explore',   'Documents',   'Related'  ]);

$(document).ready(function () {
    $("ul.first").bsPhotoGallery({
        classes: "col-xl-3 col-lg-3 col-md-3 col-sm-4",
        shortText: false
    });

    //INITIALIZER AUTOFILL
    function autocomplete(inp, arr) {
        /*the autocomplete function takes two arguments,
        the text field element and an array of possible autocompleted values:*/
        var currentFocus;
        /*execute a function when someone writes in the text field:*/
        inp.addEventListener("input", function (e) {
            var a, b, i, val = this.value;
            /*close any already open lists of autocompleted values*/
            closeAllLists();
            if (!val) {
                return false;
            }
            currentFocus = -1;
            /*create a DIV element that will contain the items (values):*/
            a = document.createElement("DIV");
            a.setAttribute("id", this.id + "autocomplete-list");
            a.setAttribute("class", "autocomplete-items");
            /*append the DIV element as a child of the autocomplete container:*/
            this.parentNode.appendChild(a);
            /*for each item in the array...*/
            for (i = 0; i < arr.length; i++) {
                /*check if the item starts with the same letters as the text field value:*/
                if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                    /*create a DIV element for each matching element:*/
                    b = document.createElement("DIV");
                    /*make the matching letters bold:*/
                    b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                    b.innerHTML += arr[i].substr(val.length);
                    /*insert a input field that will hold the current array item's value:*/
                    b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                    /*execute a function when someone clicks on the item value (DIV element):*/
                    b.addEventListener("click", function (e) {
                        /*insert the value for the autocomplete text field:*/
                        inp.value = this.getElementsByTagName("input")[0].value;
                        /*close the list of autocompleted values,
                        (or any other open lists of autocompleted values:*/
                        closeAllLists();
                    });
                    a.appendChild(b);
                }
            }
        });
        /*execute a function presses a key on the keyboard:*/
        inp.addEventListener("keydown", function (e) {
            var x = document.getElementById(this.id + "autocomplete-list");
            if (x) x = x.getElementsByTagName("div");
            if (e.keyCode == 40) {
                /*If the arrow DOWN key is pressed,
                increase the currentFocus variable:*/
                currentFocus++;
                /*and and make the current item more visible:*/
                addActive(x);
            } else if (e.keyCode == 38) { //up
                /*If the arrow UP key is pressed,
                decrease the currentFocus variable:*/
                currentFocus--;
                /*and and make the current item more visible:*/
                addActive(x);
            } else if (e.keyCode == 13) {
                /*If the ENTER key is pressed, prevent the form from being submitted,*/
                e.preventDefault();
                if (currentFocus > -1) {
                    /*and simulate a click on the "active" item:*/
                    if (x) x[currentFocus].click();
                }
            }
        });

        function addActive(x) {
            /*a function to classify an item as "active":*/
            if (!x) return false;
            /*start by removing the "active" class on all items:*/
            removeActive(x);
            if (currentFocus >= x.length) currentFocus = 0;
            if (currentFocus < 0) currentFocus = (x.length - 1);
            /*add class "autocomplete-active":*/
            x[currentFocus].classList.add("autocomplete-active");
        }

        function removeActive(x) {
            /*a function to remove the "active" class from all autocomplete items:*/
            for (var i = 0; i < x.length; i++) {
                x[i].classList.remove("autocomplete-active");
            }
        }

        function closeAllLists(elmnt) {
            /*close all autocomplete lists in the document,
            except the one passed as an argument:*/
            var x = document.getElementsByClassName("autocomplete-items");
            for (var i = 0; i < x.length; i++) {
                if (elmnt != x[i] && elmnt != inp) {
                    x[i].parentNode.removeChild(x[i]);
                }
            }
        }

        /*execute a function when someone clicks in the document:*/
        document.addEventListener("click", function (e) {
            closeAllLists(e.target);
        });
    }

    var countries = Object.keys(isoCountries);

    autocomplete(document.getElementById("location"), countries);

    // run code
    //Fill Form if provided
    var andInput = $.urlParam('andInput');
    var orInput = $.urlParam('orInput');
    var notInput = $.urlParam('notInput');
    var location = findValue(isoCountries, $.urlParam('loc'));

    var ft_search = $.urlParam('ft_search');

    var lookup = $.urlParam('lookup');

    if (andInput !== null) {
        $("#andInput").val(andInput);
    }

    if (notInput !== null) {
        $("#notInput").val(notInput);
    }

    if (orInput !== null) {
        $("#orInput").val(orInput);
    }

    if (notInput !== null) {
        $("#notInput").val(notInput);
    }

    if (location !== null) {
        $("#location").val(location);
    }

    if (ft_search !== null) {
        $("#ftsearch").val(ft_search);
    }

    if (lookup !== null) {
        if (lookup == 'snip') {
            $('.lookup-snip-btn').addClass('lookup-snip-btn-active');

            if ($('.check-if-empty-right').text() == "") {
                $('.doc-preview-pane').empty();
            }
        } else if (lookup == 'doc') {
            $('.lookup-doc-btn').addClass('lookup-doc-btn-active');
        } else if (lookup == 'clust') {
            $('.lookup-clust-btn').addClass('lookup-clust-btn-active');
        }
    } else {
        $('.lookup-clust-btn').addClass('lookup-clust-btn-active');
    }

    console.log("alpha" + $('.check-rel-doc:empty').length);
    $('.check-rel-doc').each(function (i, obj) {
        console.log($(this).text().trim().length);

        if ($(this).text().trim().length === 0) {
            console.log("here");
            $(this).parents(".rel_click").remove();
        }
    })


    // Hit highlight
    var context = document.querySelector("#the_snip_list");
    var instance = new Mark(context);
    console.log($.urlParam('ft_search'));
    instance.mark($.urlParam('ft_search'), {
        // instance.mark('McDonald', {
        accuracy: "complementary",
        ignorePunctuation: ":;.,-–—‒_(){}[]!'\"+=?!".split(""),
        wildcards: "enabled"
    });
    // Hit highlight
    var context = document.querySelector(".hlt");
    var instance = new Mark(context);
    instance.mark($.urlParam('ft_search'), {
        accuracy: "complementary",
        ignorePunctuation: ":;.,-–—‒_(){}[]!'\"+=?!".split(""),
        wildcards: "enabled"
    });
    // Remove gallery space if no images are found
    // $('.check-gallery').each(function () {
    //     if ($(this).find('img').length) {
    //         // there is an image in this div, do anything here..
    //         console.log("has image")
    //     } else {
    //         $(this).remove();
    //         console.log("no image")
    //     }
    // });

    $('.check-border:last-child').each(function () {
        $(this).css({borderRight: "0"});
    });

    // $('.check-gallery-half').each(function () {
    //     if ($(this).find('img').length) {
    //         // there is an image in this div, do anything here..
    //         console.log("has image")
    //     } else {
    //         $(this).parent().find('.may-expand').removeClass('col-md-6');
    //         $(this).parent().find('.may-expand').addClass('col-md-12');
    //         $(this).remove();
    //         console.log("no")
    //     }
    // });

    // $('.check-links-half').each(function () {
    //     if ($(this).find('a').length) {
    //         // there is an image in this div, do anything here..
    //         console.log("has link")
    //     } else {
    //         $(this).parent().find('.gallery-may-expand').removeClass('col-md-6');
    //         $(this).parent().find('.gallery-may-expand').addClass('col-md-12');
    //         $(this).remove();
    //         console.log("no")
    //     }
    // });
    // One query, example code:
});

var delayed_search_params = {
    andInput: "",
    orInput: "",
    notInput: "",
    loc: "",
    ft_search: "",
    lookup: "",
    engine: "",
    sdate: "",
    edate: ""

}

$("#ftsearch").keyup(function (event) {
    if (event.keyCode === 13) {
        full_text_search($(this).val());
    }
});

function full_text_search(val) {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);

    let lookup = urlParams.get('lookup');

    params = ""

    if (lookup !== "") params = "lookup=" + lookup;
    else params = "lookup=clust";

    dispatch_request(params + "&ft_search=" + val);
}

function lookup_document() {
    var regex = /(lookup=\w)\w+/;
    if (does_param_exists('lookup')) {
        dispatch_request(get_url_parameters().replace(regex, "lookup=doc"));
    } else {
        // if (prevent_filter_before_search()) {
        //     return;
        // } else {
        dispatch_request(get_url_parameters() + "&lookup=doc");
        // }
    }
}

function lookup_snippet() {
    var regex = /(lookup=\w)\w+/;
    if (does_param_exists('lookup')) {
        dispatch_request(get_url_parameters().replace(regex, "lookup=snip"));
    } else {
        // if (prevent_filter_before_search()) {
        //     return;
        // } else {
        dispatch_request(get_url_parameters() + "&lookup=snip");
        // }
    }
}

function lookup_cluster() {
    var regex = /(lookup=\w)\w+/;
    if (does_param_exists('lookup')) {
        dispatch_request(get_url_parameters().replace(regex, "lookup=clust"));
    } else {
        // if (prevent_filter_before_search()) {
        //     return;
        // } else {
        dispatch_request(get_url_parameters() + "&lookup=clust");
        // }
    }
}

$("#drilldown").submit(function (event) {
    // alert("Handler for .submit() called.");

    event.preventDefault();

    // If all of the inputs are empty
    if (isInputEmpty('#orInput') &&
        isInputEmpty('#andInput') &&
        isInputEmpty('#notInput') &&
        isInputEmpty('#location')) {

        alert("Must fill at least 1 input field!")
    }

    var andRex = /(andInput=\w)\w+/;
    var orRex = /(orInput=\w)\w+/;
    var notRex = /(notInput=\w)\w+/;
    var locrex = /(loc=\w)\w+/;

    var andInput, orInput, notInput, location = ""
    var existing_url_params = get_url_parameters()

    if (!isInputEmpty('#andInput')) {
        if (does_param_exists(andRex)) {
            existing_url_params = existing_url_params.replace(andRex, "andInput=" + getInputVal('#andInput'));
        } else {
            existing_url_params = existing_url_params + "&andInput=" + getInputVal('#andInput');
        }
    }

    if (!isInputEmpty('#orInput')) {
        if (does_param_exists(orRex)) {
            existing_url_params = existing_url_params.replace(orRex, "orInput=" + getInputVal('#orInput'));
        } else {
            existing_url_params = existing_url_params + "&orInput=" + getInputVal('#orInput');
        }
    }

    if (!isInputEmpty('#notInput')) {
        if (does_param_exists(notRex)) {
            existing_url_params = existing_url_params.replace(notRex, "notInput=" + getInputVal('#notInput'));
        } else {
            existing_url_params = existing_url_params + "&notInput=" + getInputVal('#notInput');
        }
    }

    if (!isInputEmpty('#location')) {
        iso_2_location = getCountryName(getInputVal('#location'));
        if (does_param_exists(locrex)) {
            existing_url_params = existing_url_params.replace(locrex, "loc=" + iso_2_location);
        } else {
            existing_url_params = existing_url_params + "&loc=" + iso_2_location;
        }
    }

    console.log(location);

    if (prevent_filter_before_search()) {
        return;
    } else {
        dispatch_request(existing_url_params);
    }
});

function prevent_filter_before_search() {
    if (isInputEmpty('#ftsearch')) {
        alert("Before filtering, please initiate the search from the full-text search panel");
        return true;
    } else {
        return false;
    }
}

function isInputEmpty(id) {
    return !$(id).val().trim();
}

function getInputVal(id) {
    return $(id).val().trim();
}

$('.rel_click, .doc-title, .doc-title-click, a').click(function () {
    var lookup = $.urlParam('lookup');
    var targ = 0;

    if ($(this).hasClass('doc-title') || $(this).is('a') || $(this).hasClass('doc-title-click')) {
        targ = $(this);
    } else if (lookup === 'doc') {
        targ = $(this).parent().find('.cluster-result').find('.doc-title');
    } else {
        targ = $(this).parent().find('.cluster-result').find('.cluster-title');
    }

    console.log(targ);
    console.log($(this).id);
    // console.log($(this).parent().id);
    // console.log(targ.id);

    var hex = targ.css('color');

    console.log(hex);
    var lum = -.20;

    // validate hex string
    hex = String(hex).replace(/[^0-9a-f]/gi, '');
    if (hex.length < 6) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }
    lum = lum || 0;

    // convert to decimal and change luminosity
    var rgb = "#", c, i;
    for (i = 0; i < 3; i++) {
        c = parseInt(hex.substr(i * 2, 2), 16);
        c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16);
        rgb += ("00" + c).substr(c.length);
    }

    targ.css('color', rgb);

    return rgb;
})
// var targ = $(this).parent().find('.cluster-result').find('.cluster-title');
// console.log(obj.id);
// console.log(obj.parent().id);
// console.log(targ.id);
//
// var hex = targ.css('color');
//
// console.log(hex);
// var lum = -.20;
//
// // validate hex string
// hex = String(hex).replace(/[^0-9a-f]/gi, '');
// if (hex.length < 6) {
// 	hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
// }
// lum = lum || 0;
//
// // convert to decimal and change luminosity
// var rgb = "#", c, i;
// for (i = 0; i < 3; i++) {
// 	c = parseInt(hex.substr(i*2,2), 16);
// 	c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16);
// 	rgb += ("00"+c).substr(c.length);
// }
//
// targ.css('color', rgb);
//
// return rgb;
// }

// $(window).on('load', function () {
//     console.log("here in load");
//     // Remove gallery space if no images are found
//     $('.check-gallery').each(function () {
//         if ($(this).find('img').length) {
//             // there is an image in this div, do anything here..
//             console.log("has image")
//         } else {
//             $(this).remove();
//             console.log("no image")
//         }
//     });
//
//     $('.check-border:last-child').each(function () {
//         $(this).css({borderRight: "0"});
//     });
//
//     $('.check-gallery-half').each(function () {
//         if ($(this).find('img').length) {
//             // there is an image in this div, do anything here..
//             console.log("has image")
//         } else {
//             $(this).parent().find('.may-expand').removeClass('col-md-6');
//             $(this).parent().find('.may-expand').addClass('col-md-12');
//             $(this).remove();
//             console.log("no")
//         }
//     });
//
//     $('.check-links-half').each(function () {
//         if ($(this).find('a').length) {
//             // there is an image in this div, do anything here..
//             console.log("has link")
//         } else {
//             $(this).parent().find('.gallery-may-expand').removeClass('col-md-6');
//             $(this).parent().find('.gallery-may-expand').addClass('col-md-12');
//             $(this).remove();
//             console.log("no")
//         }
//     });
// })