import sys
import sys

def detect_failure(log_file, count_limit):
    d_failures = {}  # 故障状態のサーバと故障期間を格納する辞書

    with open(log_file, 'r') as file:
        l_lines = file.readlines()
    #print("file open")

    for line in l_lines:
        l_parts = line.split(',')
        timestamp = l_parts[0].strip()
        server_address = l_parts[1].strip()
        response_time = l_parts[2].strip()
        #print(timestamp,server_address,response_time)

        if response_time == '-':  # タイムアウトの場合
            #print("failure found") # 故障発見通知
            if server_address not in d_failures:  # サーバが初めて故障した場合
                d_failures[server_address] = {'start_time': timestamp, 'end_time': None, 'count':1}
            else:  # サーバー故障が2度目の場合
                if server_address in d_failures:  # サーバが故障中である場合
                    d_failures[server_address]['count'] += 1
                    if int(d_failures[server_address]['count']) >= int(count_limit):
                        d_failures[server_address]['end_time'] = timestamp
                        # 故障期間を出力するならここで出力
                        print(f"サーバ {server_address} は {d_failures[server_address]['start_time']} から {timestamp} 間 故障しています。")
        elif server_address in d_failures: # 故障が解消された場合
            del d_failures[server_address]  # サーバの故障情報を削除

    # 故障が終了していないサーバの情報を出力
    for server, failure_info in d_failures.items():
        print(f"サーバ {server} は {failure_info['start_time']} から現在まで故障しています。")

    file.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:No file designation python server_ping_check.py <file_path>")
    else:
        file_path = sys.argv[1]
        count_limit = sys.argv[2]
        detect_failure(file_path,count_limit)
