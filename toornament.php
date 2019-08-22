<!DOCTYPE html>
<html>
<body>

  <?php
  $curl = curl_init();

  // 1. Getting an access token
  curl_setopt_array(
    $curl, array(
      CURLOPT_URL
        => 'https://api.toornament.com/oauth/v2/token?grant_type=client_credentials&client_id=R4kxuPAlmRBF5zU3ehwhy6dH9pqVTMW9NAk9FQ4I&client_secret=8TnKawgG6yCtmiiyGSasR5VJJ0DDFGuMP2eH3ZJL',
      CURLOPT_RETURNTRANSFER
        => true,
      CURLOPT_VERBOSE
        => true,
      CURLOPT_HEADER
        => true,
      CURLOPT_SSL_VERIFYPEER
        => false,
      CURLOPT_HTTPHEADER
        => array(
        'X-Api-Key: HpI0hNoJDqYm_RaRT1CSLHoUCLwQPVbVeJRfTFOC3zc',
        'Content-Type: application/json'
  )));
  $output
    = curl_exec($curl);
  $header_size
    = curl_getinfo($curl, CURLINFO_HEADER_SIZE);
  $header
    = substr($output, 0, $header_size);
  $body
    = json_decode(substr($output, $header_size));
  $access_token
    = $body->access_token;

  // 2. Getting your tournaments
  curl_setopt_array(
      $curl, array(
      CURLOPT_URL
              => 'https://api.toornament.com/v1/me/tournaments/',
      CURLOPT_RETURNTRANSFER  => true,
      CURLOPT_SSL_VERIFYPEER  => false,
      CURLOPT_HTTPHEADER      => array(
          'X-Api-Key: HpI0hNoJDqYm_RaRT1CSLHoUCLwQPVbVeJRfTFOC3zc',
          'Authorization: Bearer '.$access_token,
          'Content-Type: application/json'
      )));
  $output
          = curl_exec($curl);$header_size
      = curl_getinfo($curl, CURLINFO_HEADER_SIZE);
  $header
          = substr($output, 0, $header_size);
  $body
            = json_decode(substr($output, $header_size));
  var_dump($body);

  // 3. Setting a match result
  $data = '{
    "status": "completed",
    "opponents": [
        {
            "number": 1,
            "result": 1,
            "score": 16,
            "forfeit": false
        },
        {
            "number": 2,
            "result": 3,
            "score": 12,
            "forfeit": false
        }
  ]}';
  curl_setopt_array(
    $curl, array(
      CURLOPT_URL
              => 'https://api.toornament.com/v1/tournaments/{TOURNAMENT_ID}/matches/{MATCH_ID}/result',
      CURLOPT_RETURNTRANSFER  => true,
      CURLOPT_SSL_VERIFYPEER  => false,
      CURLOPT_HTTPHEADER
        => array(
          'X-Api-Key: HpI0hNoJDqYm_RaRT1CSLHoUCLwQPVbVeJRfTFOC3zc',
          'Authorization: Bearer '.$access_token,
          'Content-Type: application/json'
      ),
      CURLOPT_CUSTOMREQUEST
        => 'PUT',
      CURLOPT_POSTFIELDS
        => $data
  ));
  $output
    = curl_exec($curl);
  $header_size
    = curl_getinfo($curl, CURLINFO_HEADER_SIZE);
  $header
    = substr($output, 0, $header_size);
  $body
    = json_decode(substr($output, $header_size));
  var_dump($body);

  // Close request to clear up some resources
  curl_close($curl);

  echo "My first PHP script!";
  ?>

</body>
</html>