angular
  .module('MyApp',['ngMaterial'])
  .controller('AppCtrl', function ($scope, $timeout, $mdSidenav, $http, $window) {
    var ctrl = this;
    CTRL = ctrl;

    console.log("Hello Angular")
    $scope.toggleLeft = buildToggler('left');
    $scope.toggleRight = buildToggler('right');

    ctrl.streamOff = true;


    $window.onbeforeunload = function (evt) {
                ctrl.streamOff = true;
            };


    function buildToggler(componentId) {
      return function() {
        $mdSidenav(componentId).toggle();
      };
    };

    $scope.setCamera = function(){
      ctrl.streamOff = true;
      choice = $scope.cameraChoice
      $http(
        {
        method: "GET",
        url: "/set_camera/".concat(choice)
      })
      .then(
        function successCallback(response) {
        console.log(response.data.success)
        if (response.data.success == true){
            ctrl.streamOff = false;
            console.log("Successfully changed camera channel!");
        }
        else{
        console.log("No signal on this camera channel!");
        }
      }
      , function errorCallback(response) {
        console.log("Failed to communicate with server.");
      });
    };


    $scope.setImagingParameters = function(){
      exposure = 1.0 / $scope.exposure * 15000
      $http(
        {
        method: "GET",
        url: "/set_imaging_parameters/".concat(exposure)
      })
    };


  })

  .config(function($mdThemingProvider) {
    $mdThemingProvider.theme('default')
      .dark()
      .primaryPalette('blue-grey')
      .accentPalette('grey')
      .warnPalette('red');
  });