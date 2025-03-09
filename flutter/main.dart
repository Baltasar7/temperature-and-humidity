import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';

final String OBJS_GET_URL='';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        appBar: AppBar(title: Text('気温と湿度')),
        body: DataFetcherScreen(),
      ),
    );
  }
}

class DataFetcherScreen extends StatefulWidget {
  @override
  _DataFetcherScreenState createState() => _DataFetcherScreenState();
}

class _DataFetcherScreenState extends State<DataFetcherScreen> {
  final TextEditingController _startDateController = TextEditingController();
  final TextEditingController _endDateController = TextEditingController();
  List<dynamic> _getDataList = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    fetchLastThreeDaysData();
  }

  Map<String, String> getLastThreeDaysRange() {
    final now = DateTime.now();
    final startDate = now.subtract(Duration(days: 2));
    return {
      "startDate": DateFormat('yyyyMMdd').format(startDate),
      "endDate": DateFormat('yyyyMMdd').format(now),
    };
  }

  Future<void> fetchData({required String startDate, required String endDate}) async {
    setState(() => _isLoading = true);

    final url = Uri.parse('$OBJS_GET_URL?startDate=$startDate&endDate=$endDate');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      setState(() {
        _getDataList = json.decode(response.body);
        _getDataList = _getDataList.reversed.toList();
        _isLoading = false;
      });
    } else {
      print("Failed to load data");
      setState(() => _isLoading = false);
    }
  }

  Future<void> fetchLastThreeDaysData() async {
    final range = getLastThreeDaysRange();
    await fetchData(startDate: range["startDate"]!, endDate: range["endDate"]!);
  }

  Future<void> fetchUserSpecifiedData() async {
    if (_startDateController.text.isEmpty || _endDateController.text.isEmpty) return;
    await fetchData(startDate: _startDateController.text, endDate: _endDateController.text);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _startDateController,
                    decoration: InputDecoration(
                      labelText: "開始日(YYYYMMDD)",
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                SizedBox(width: 10),
                Expanded(
                  child: TextField(
                    controller: _endDateController,
                    decoration: InputDecoration(
                      labelText: "終了日(YYYYMMDD)",
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                SizedBox(width: 10),
                ElevatedButton(
                  onPressed: fetchUserSpecifiedData,
                  child: Text('取得'),
                ),
              ],
            ),
            SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                itemCount: _getDataList.length,
                itemBuilder: (context, index) {
                  final data = _getDataList[index];
                  final timestamp = data['timestamp'];
                  final temperature = data['temperature'];
                  final humidity = data['humidity'];
                  return ListTile(
                    title: Text('$timestamp'),
                    subtitle: Text('気温: $temperature°C, 湿度: $humidity%'),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}