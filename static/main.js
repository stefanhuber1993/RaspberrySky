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
      console.log("Test");
      $http(
        {
        method: "GET",
        url: "/set_camera/".concat(choice)
      })
      .then(
        function successCallback(response) {
        ctrl.streamOff = false;
        console.log("Successfully changed camera channel!");
      }
      , function successCallback(response) {
        console.log("Failed to change camera channel!");
      });
    };

  })

  .config(function($mdThemingProvider) {
    $mdThemingProvider.theme('default')
      .dark()
      .primaryPalette('blue-grey')
      .accentPalette('grey')
      .warnPalette('red');
  });