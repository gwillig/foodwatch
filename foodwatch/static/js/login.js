        function check_connection(){
        /*
        If mobile network is below 2g it should show the img instead of the video works only for CHROME
        */
        try{
            let network_status = navigator.connection.effectiveType;
            if(network_status == '2g' || network_status == 'slow-2g'){
                //Remove video if connection is to slow
                document.querySelector("video source").src=""
            }}
            catch(err) {
              //Nothing will happen
            }


        }

        function change_redirect(){
            /*
            @description:
                Change the auth0 redirect. If the url contain localhost it change it to localhost
            */

            let current_url = window.location.href
            let href='https://gwillig.eu.auth0.com/authorize?audience=foodwatchgw&response_type=token&client_id=YwBpDwZuXEuTNS5NKDJ54HR6DTOQN04l'

            if (current_url.includes("localhost:5000")){
                document.querySelector("#loginlink").href = href + "&redirect_uri=http://localhost:5000/home"
            }
            //Addresse of the testserver if a selenium test is running
            else if(current_url.includes("localhost:7000")){
                document.querySelector("#loginlink").href = href + "&redirect_uri=http://localhost:7000/home"
            }
            else {
                document.querySelector("#loginlink").href = href + "&redirect_uri=https://foodwatchgw.herokuapp.com/home"
            }
        }