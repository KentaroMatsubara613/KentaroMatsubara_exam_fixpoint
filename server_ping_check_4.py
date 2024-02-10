import sys
import ipaddress

def classify_network(ip_address, subnet_mask):
    # IPアドレスとサブネットマスクを合成してネットワークアドレスを取得
    network_address = ipaddress.IPv4Network(ip_address + '/' + subnet_mask, strict=False)
    return network_address

def detect_failure(p1):
    d_failures = {}  # 故障状態のサーバと故障期間を格納する辞書
    d_response = {}
    ll_server_ping = [] # サーバ応答時間を格納するリスト
    ll_server_timelog = []
    server_cnt = 0

    with open(p1.file_path, 'r') as file:
        l_lines = file.readlines()
        #print("file open")

    for s_line in l_lines:
        #ログ解析
        l_parts = s_line.split(',')
        timestamp = l_parts[0].strip()
        server_address = l_parts[1].strip()
        response_time = l_parts[2].strip()
        if p1.flag == 'network':  # ネットワーク応答時間チェック
            ip_address, subnet_mask = server_address.split('/')
            server_address =  classify_network(ip_address, subnet_mask) # ネットワークアドレスでIPアドレスを置き換え、以下同処理

        else:
            # サーバ応答時間チェック
            if response_time == '-':  # サーバ応答がない場合、値999とする
                ping_time = int(999)
            else:
                ping_time = int(response_time)
            if server_address not in d_response: # 新規サーバの登録
                d_response[server_address] = {'list_index':server_cnt}
                ll_server_ping.append([server_cnt,ping_time])
                ll_server_timelog.append([server_cnt,timestamp])
                server_num = server_cnt
                server_cnt += 1
            else:
                server_num = d_response[server_address]['list_index'] # サーバ番号読み込み
                ll_server_ping[server_num].insert(1,ping_time)  # サーバ応答時間を格納
                ll_server_timelog[server_num].insert(1,timestamp)  # 時刻を格納
            if (len(ll_server_timelog[server_num])-1) == p1.average_cnt:  # 直近の所定回数の場合
                ave = sum(ll_server_ping[server_num])/len(ll_server_ping[server_num])
                if ave > p1.busy_ping:
                    print(f"サーバ {server_address} は過負荷状態です。(平均応答ping: {round(ave,1)})")
                    print(f"過負荷状態期間 {ll_server_timelog[server_num][-1]} から {ll_server_timelog[server_num][1]} 間")
                ll_server_ping[server_num].pop() #　古い応答時間情報を消去
                ll_server_timelog[server_num].pop()
                
        #サーバタイムアウトチェック
        if response_time == '-':  # タイムアウトの場合
            #print("failure found") # 故障発見通知（テスト用）
            if server_address not in d_failures:  # サーバが初めて故障した場合
                d_failures[server_address] = {'start_time': timestamp, 'end_time': None, 'count':1}
            else:  # サーバー故障が2度目の場合
                if server_address in d_failures:  # サーバが故障中である場合
                    d_failures[server_address]['count'] += 1
                    if int(d_failures[server_address]['count']) >= int(p1.count_limit):
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
    if len(sys.argv) != 6:
        sys.exit("Usage: parameters err")
    else:

        class parameters: #エラー条件用パラメータ
            pass
        p1 = parameters()
        p1.file_path = sys.argv[1]
        p1.count_limit = sys.argv[2]
        p1.busy_ping = int(sys.argv[3])
        p1.average_cnt = int(sys.argv[4])
        if sys.argv[5] == 'network':
            p1.flag = sys.argv[5]
        else:
            sys.exit("Usage: parameters err")
        
        detect_failure(p1)
