let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    // here id_address is added by django forms to identify address field
    document.getElementById('id_address'),
    {
        // geocode means address, establishment are business addresses like hotels, restaurants, offices
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code. We can other countries as well
        componentRestrictions: {'country': ['in']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        // console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
    // console.log(place);
    var geocoder = new google.maps.Geocoder();
    var address = document.getElementById('id_address').value;
    // console.log(address)
    // result has address data and status is api call status
    geocoder.geocode({'address': address}, function(results, status){
        // console.log('results=', results); 
        // console.log('status=', status);
        if(status == google.maps.GeocoderStatus.OK){
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();
            // console.log('lat=', latitude)
            // console.log('lng=', longitude)
            // places the values of lat and lng in the django form
            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);

            $('#id_address').val(address);
        }
    });

    // loop through the address components and assign other address data
    // console.log(place.address_components);
    for(var i=0; i<place.address_components.length; i++){
        for(var j=0; j<place.address_components[i].types.length; j++){
            // get country
            if(place.address_components[i].types[j] == 'country'){
                var country = place.address_components[i].long_name;
                $('#id_country').val(country);
            }
            // get state
            if(place.address_components[i].types[j] == 'administrative_area_level_1'){
                var state = place.address_components[i].long_name;
                $('#id_state').val(state);
            }
            // get city
            if(place.address_components[i].types[j] == 'locality'){
                var city = place.address_components[i].long_name;
                $('#id_city').val(city);
            }
            // get pincode
            if(place.address_components[i].types[j] == 'postal_code'){
                var pin_code = place.address_components[i].long_name;
                $('#id_pin_code').val(pin_code);
            }else{
                $('#id_pin_code').val("");
            }
        }
    } 
}

$(document).ready(function(){
    //add to cart
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();
        
        food_id =  $(this).attr('data-id');
        url = $(this).attr('data-url');

        // send food id to view using ajax request
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response)
                if(response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login';
                    });
                }else if(response.status == 'Failed'){
                    swal(response.message, '', 'error');
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty)
                }
            }
        });
    });


    //place the cart item quantity on load
    $('.item_qty').each(function(){
        var the_id = $(this).attr('id');
        var qty = $(this).attr('data-qty');
        // console.log(qty)

        $('#'+the_id).html(qty)
    });

    //decrease cart
    $('.decrease_cart').on('click', function(e){
        e.preventDefault();
        
        food_id =  $(this).attr('data-id');
        url = $(this).attr('data-url');

        // send food id to view using ajax request
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response)
                if(response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login';
                    });
                }else if(response.status == 'Failed'){
                    swal(response.message, '', 'error');
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty)
                }
            }
        });
    });

});