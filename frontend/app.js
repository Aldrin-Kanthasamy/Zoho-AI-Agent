angular.module('aiAgentApp', [])
  .controller('MainController', function($scope, $http) {
    $scope.dashboard = {users: [], tasks: [], tickets: []};
    $scope.health = 'unknown';

    $scope.refresh = function() {
      $http.get('http://localhost:8000/superadmin/dashboard').then(function(resp){
        $scope.dashboard = resp.data;
      });
      $http.get('http://localhost:8000/health').then(function(resp){
        $scope.health = resp.data.status + ' @ ' + resp.data.time;
      });
    };

    $scope.userId = null;
    $scope.userDashboard = null;
    $scope.fetchUserDashboard = function() {
      if (!$scope.userId) {
        $scope.userDashboard = 'Select user id';
        return;
      }
      $http.get('http://localhost:8000/users/' + $scope.userId + '/dashboard').then(function(resp){
        $scope.userDashboard = resp.data;
      }, function(err){
        $scope.userDashboard = 'Error: ' + (err.data ? err.data.detail : err.statusText);
      });
    };

    $scope.nlSubmit = function() {
      $http.post('http://localhost:8000/admin/query', {text: $scope.nlQuery}).then(function(resp){
        $scope.nlResult = JSON.stringify(resp.data);
        $scope.refresh();
      }, function(err){ $scope.nlResult = 'Error: ' + err.status; });
    };

    $scope.createDemoTask = function() {
      var payload = {
        external_id: 'demo-task-' + Date.now(),
        title: 'Full Stack feature implementation',
        description: 'Implement feature for frontend and backend',
        skill_needed: 'Full Stack',
        priority: 'High'
      };
      $http.post('http://localhost:8000/webhook/zohosprint', payload).then(function(resp){
        $scope.demoResult = 'Sprint task created: ' + JSON.stringify(resp.data);
        $scope.refresh();
      });
    };

    $scope.createDemoTicket = function() {
      var payload = {
        external_id: 'demo-ticket-' + Date.now(),
        subject: 'Incident: login fails',
        description: 'User cannot login due to 500 error',
        skill_needed: 'Backend',
        priority: 'Urgent'
      };
      $http.post('http://localhost:8000/webhook/zohodesk', payload).then(function(resp){
        $scope.demoResult = 'Desk ticket created: ' + JSON.stringify(resp.data);
        $scope.refresh();
      });
    };

    $scope.generateStandup = function() {
      $http.post('http://localhost:8000/admin/query', {text: 'generate daily standup'}).then(function(resp){
        $scope.standupResult = JSON.stringify(resp.data);
      });
    };

    $scope.fetchStandup = function() {
      $http.get('http://localhost:8000/standup/latest').then(function(resp){
        $scope.standupLatest = resp.data.content;
      }, function(err){
        $scope.standupLatest = 'Error: ' + (err.data ? err.data.detail : err.statusText);
      });
    };

    $scope.refresh();
  });
