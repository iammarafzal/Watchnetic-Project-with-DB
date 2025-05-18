// to get current year
function getYear() {
    var currentDate = new Date();
    var currentYear = currentDate.getFullYear();
    document.querySelector("#displayYear").innerHTML = currentYear;
}

getYear();

// client section owl carousel
$(".client_owl-carousel").owlCarousel({
    loop: true,
    margin: 20,
    dots: false,
    nav: true,
    navText: [],
    autoplay: true,
    autoplayHoverPause: true,
    navText: [
        '<i class="fa fa-angle-left" aria-hidden="true"></i>',
        '<i class="fa fa-angle-right" aria-hidden="true"></i>'
    ],
    responsive: {
        0: {
            items: 1
        },
        768: {
            items: 2
        }
    }
});

/** google_map js **/

function myMap() {
    var mapProp = {
        center: new google.maps.LatLng(40.712775, -74.005973),
        zoom: 18,
    };
    var map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
}

$(document).ready(function() {
    console.log("FAQ script loaded"); // Debugging line
    
    // FAQ Toggle functionality
    $('.faq_question').on('click', function() {
        console.log("FAQ question clicked"); // Debugging line
        
        let $item = $(this).parent('.faq_item');
        
        if ($item.hasClass('active')) {
            // Close this item
            $item.removeClass('active');
        } else {
            // Close all items and open this one
            $('.faq_item').removeClass('active');
            $item.addClass('active');
        }
    });
});