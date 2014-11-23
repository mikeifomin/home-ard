angular
    .module('myApp', [])

angular
    .module('myApp').service("metricsService", function($q, $http){


        var chart = new Highcharts.StockChart( {

            chart: {
              type: 'spline',
              renderTo: angular.element('#container')[0]
            },
            rangeSelector : {
                selected : 1
            },

            title : {
                text : 'Отопление'
            },
            yAxis: {
                type: 'datetime'
            },

        });

        var currentMetrics = {
Temp0: 36.94,
Temp1: 30.62,
Temp2: 22.00,
Temp3: 21.87,
Temp4: 65.87,
Temp5: 72.87,
Temp6: 72.44,
Temp7: 35.44,
Message: "measures ok. Calculating PID",
SetUpPol: 40.00,
PolKp: 1000.00,
PolKi: 1.00,
PolKd: 1.00,
PolSampleTime: 5000.00,
dSetPointPol: 36.75,
dInputPol: 36.94,
OutputPol: -135.00,
Skip: 0,



        }
     return {
            chart:chart,
            getCurrentMetrics:function(){
                var result = []
                _.forEach(currentMetrics,function(value,key){
                console.log(key);
                    result.push({value:value,id:key})
                })
                return result
            },
            askCurrentMetrics:function(){
                    $http.get("/get_state").success(function(data){
                        currentMetrics = data
                    })
            }
     }

    })


angular
    .module('myApp').controller("all", function($scope, $q, $http, $interval, metricsService){
        metricsService.chart;
        $scope.metrics = metricsService.getCurrentMetrics();
        $interval(function(){
            metricsService.askCurrentMetrics()
            $scope.metrics = metricsService.getCurrentMetrics();
        },500)
        $scope.seriesVisible = {};

        $scope.$watchCollection("seriesVisible",function(newVal,oldVal){
            console.log(33,oldVal,newVal);
            _.forEach(newVal,function(value,key){

                    var series = metricsService.chart.get(key);
                    if (series){
                    if (value){
                        series.show();
                    } else {
                        series.hide();

                    }}

            });


        })
        $http.get("/get_history").success(function(resp){
            data = [];

            serieses = {};

            _.forEach(resp,function(item){

                    timestamp = item.timestamp;
                    _.forEach(item,function(value,key){
                        if (!serieses[key]) {
                            serieses[key] = [];
                        }
                        if (key != "timestamp"){
                            serieses[key].push([timestamp*1000,value])
                        }
                    })
            })
            _.forEach(serieses,function(value,key){
            $scope.seriesVisible[key] = false;
                metricsService.chart.addSeries({
                    name:key,
                    id:key,
                    data:value,
                })
                metricsService.chart.get(key).hide();


            })

        })
    })

