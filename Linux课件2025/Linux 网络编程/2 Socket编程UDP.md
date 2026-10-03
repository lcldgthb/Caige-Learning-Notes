2Socket编程UDP

UDP⽹络编程

V1版本-Echoserver

简单的回显服务器和客⼾端代码

备注:代码中会⽤到地址转换函数.参考接下来的章节.

nocopy.hpp

1

2

3

4

5

6

7

8

9

10

11

#pragma once

#include <iostream>

class nocopy

{

public:

    nocopy(){}

    nocopy(const nocopy &) = delete;

    const nocopy& operator = (const nocopy &) = delete;

    ~nocopy(){}

};

UdpServer.hpp

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

#pragma once

#include <iostream>

#include <string>

#include <cerrno>

#include <cstring>

#include <unistd.h>

#include <strings.h>

#include <sys/types.h>

#include <sys/socket.h>

#include <netinet/in.h>

#include <arpa/inet.h>

#include "nocopy.hpp"

#include "Log.hpp"

#include "Comm.hpp"

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

54

55

56

57

58

59

#include "InetAddr.hpp"

const static uint16_t defaultport = 8888;

const static int defaultfd = -1;

const static int defaultsize = 1024;

class UdpServer : public nocopy

{

public:

    UdpServer(uint16_t port = defaultport)

        : _port(port), _sockfd(defaultfd)

    {

    }

    void Init()

    {
        // 1. 创建socket，就是创建了⽂件细节
        _sockfd = socket(AF_INET, SOCK_DGRAM, 0);

        if (_sockfd < 0)

        {

            lg.LogMessage(Fatal, "socket errr, %d : %s\n", errno,

strerror(errno));

            exit(Socket_Err);

        }

        lg.LogMessage(Info, "socket success, sockfd: %d\n", _sockfd);

        // 2. 绑定，指定⽹络信息
        struct sockaddr_in local;

        bzero(&local, sizeof(local)); // memset

        local.sin_family = AF_INET;

        local.sin_port = htons(_port);

        local.sin_addr.s_addr = INADDR_ANY; // 0

        // local.sin_addr.s_addr = inet_addr(_ip.c_str()); // 1. 4字节IP 2. 变
成⽹络序列

        // 结构体填完，设置到内核中了吗？？没有
        int n = ::bind(_sockfd, (struct sockaddr *)&local, sizeof(local));

        if (n != 0)

        {

            lg.LogMessage(Fatal, "bind errr, %d : %s\n", errno,

strerror(errno));

            exit(Bind_Err);

        }

    }

    void Start()

    {

60

61

62

63

64

65

66

67

68

69

70

71

        // 服务器永远不退出
        char buffer[defaultsize];

        for (;;)

        {

            struct sockaddr_in peer;
            socklen_t len = sizeof(peer); // 不能乱写
            ssize_t n = recvfrom(_sockfd, buffer, sizeof(buffer) - 1, 0,

(struct sockaddr *)&peer, &len);

            if (n > 0)

            {

                InetAddr addr(peer);

                buffer[n] = 0;

                std::cout << "[" << addr.PrintDebug() << "]# " << buffer <<

std::endl;

72

                sendto(_sockfd, buffer, strlen(buffer), 0, (struct sockaddr

*)&peer, len);

            }

        }

    }

    ~UdpServer()

    {

    }

private:
    // std::string _ip; // 后⾯要调整
    uint16_t _port;

    int _sockfd;

};

73

74

75

76

77

78

79

80

81

82

83

84

InetAddr.hpp

1

2

3

4

5

6

7

8

9

10

11

12

13

14

#pragma once

#include <iostream>

#include <string>

#include <sys/types.h>

#include <sys/socket.h>

#include <netinet/in.h>

#include <arpa/inet.h>

class InetAddr

{

public:

    InetAddr(struct sockaddr_in &addr):_addr(addr)

    {

        _port = ntohs(_addr.sin_port);

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

        _ip = inet_ntoa(_addr.sin_addr);

    }

    std::string Ip() {return _ip;}

    uint16_t Port() {return _port;};

    std::string PrintDebug()

    {

        std::string info = _ip;

        info += ":";

        info += std::to_string(_port);  // "127.0.0.1:4444"

        return info;

    }

    ~InetAddr(){}

private:

    std::string _ip;

    uint16_t _port;

    struct sockaddr_in _addr;

};

Comm.hpp

1

2

3

4

5

6

7

#pragma once

enum{

    Usage_Err = 1,

    Socket_Err,

    Bind_Err

};

•

Log.hpp 已经有了，这⾥就不再复制粘贴了

• 云服务器不允许直接bind公有IP，我们也不推荐编写服务器的时候，bind明确的IP，推荐直接写成

INADDR_ANY

1

2

/* Address to accept any incoming messages.  */

#define INADDR_ANY    ((in_addr_t) 0x00000000)

在⽹络编程中，当⼀个进程需要绑定⼀个⽹络端⼝以进⾏通信时，可以使⽤INADDR_ANY作为IP地址

参数。这样做意味着该端⼝可以接受来⾃任何IP地址的连接请求，⽆论是本地主机还是远程主机。例

如，如果服务器有多个⽹卡（每个⽹卡上有不同的IP地址），使⽤INADDR_ANY可以省去确定数据是

从服务器上具体哪个⽹卡/IP地址上⾯获取的。

UdpClient.hpp

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

#include <iostream>

#include <cerrno>

#include <cstring>

#include <string>

#include <unistd.h>

#include <sys/types.h> /* See NOTES */

#include <sys/socket.h>

#include <arpa/inet.h>

#include <netinet/in.h>

void Usage(const std::string &process)

{

    std::cout << "Usage: " << process << " server_ip server_port" <<

std::endl;

}

// ./udp_client server_ip server_port

int main(int argc, char *argv[])

{

    if (argc != 3)

    {

        Usage(argv[0]);

        return 1;

    }

    std::string serverip = argv[1];

    uint16_t serverport = std::stoi(argv[2]);

    // 1. 创建socket
    int sock = socket(AF_INET, SOCK_DGRAM, 0);

    if (sock < 0)

    {

        std::cerr << "socket error: " << strerror(errno) << std::endl;

        return 2;

    }

    std::cout << "create socket success: " << sock << std::endl;

    // 2. client要不要进⾏bind? ⼀定要bind的！！
    // 但是，不需要显⽰bind，client会在⾸次发送数据的时候会⾃动进⾏bind
    // 为什么？server端的端⼝号，⼀定是众所周知，不可改变的，client 需要 port，bind随
机端⼝.
    // 为什么？client会⾮常多.
    // client 需要bind，但是不需要显⽰bind，让本地OS⾃动随机bind，选择随机端⼝号
    // 2.1 填充⼀下server信息
    struct sockaddr_in server;

    memset(&server, 0, sizeof(server));

45

46

47

48

49

50

51

52

53

54

55

56

57

58

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

76

77

78

    server.sin_family = AF_INET;

    server.sin_port = htons(serverport);

    server.sin_addr.s_addr = inet_addr(serverip.c_str());

    while (true)

    {
        // 我们要发的数据
        std::string inbuffer;

        std::cout << "Please Enter# ";

        std::getline(std::cin, inbuffer);
        // 我们要发给谁呀？server
        ssize_t n = sendto(sock, inbuffer.c_str(), inbuffer.size(), 0, (struct

 sockaddr*)&server, sizeof(server));

        if(n > 0)

        {

            char buffer[1024];
            //收消息
            struct sockaddr_in temp;

            socklen_t len = sizeof(temp);

            ssize_t m = recvfrom(sock, buffer, sizeof(buffer)-1, 0, (struct
sockaddr*)&temp, &len); // ⼀般建议都是要填的.
            if(m > 0)

            {

                buffer[m] = 0;

                std::cout << "server echo# " << buffer << std::endl;

            }

            else

                break;

        }

        else

            break;

    }

    close(sock);

    return 0;

}

• client端要不要显⽰bind的问题

V2版本-DictServer

实现⼀个简单的英译汉的⽹络字典

dict.txt

1

apple: 苹果

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

banana: ⾹蕉
cat: 猫
dog: 狗
book: 书
pen: 笔
happy: 快乐的
sad: 悲伤的
run: 跑
jump: 跳
teacher: ⽼师
student: 学⽣
car: 汽⻋
bus: 公交⻋
love: 爱
hate: 恨
hello: 你好
goodbye: 再⻅
summer: 夏天
winter: 冬天

Dict.hpp

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

#pragma once

#include <iostream>

#include <string>

#include <fstream>

#include <unordered_map>

const std::string sep = ": ";

class Dict

{

private:

    void LoadDict()

    {

        std::ifstream in(_confpath);

        if(!in.is_open())

        {
            std::cerr << "open file error" << std::endl; // 后⾯可以⽤⽇志替代打
印
            return;

        }

        std::string line;

        while(std::getline(in, line))

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

        {

            if(line.empty()) continue;

            auto pos = line.find(sep);

            if(pos == std::string::npos) continue;

            std::string key = line.substr(0, pos);

            std::string value = line.substr(pos + sep.size());

            _dict.insert(std::make_pair(key, value));

        }

        in.close();

    }

public:

    Dict(const std::string &confpath):_confpath(confpath)

    {

        LoadDict();

    }

    std::string Translate(const std::string &key)

    {

        auto iter = _dict.find(key);

        if(iter == _dict.end()) return std::string("Unknown");

        else return iter->second;

    }

    ~Dict()

    {}

private:

    std::string _confpath;

    std::unordered_map<std::string, std::string> _dict;

};

UdpServer.hpp

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

#pragma once

#include <iostream>

#include <string>

#include <cerrno>

#include <cstring>

#include <unistd.h>

#include <strings.h>

#include <sys/types.h>

#include <sys/socket.h>

#include <netinet/in.h>

#include <arpa/inet.h>

#include <unordered_map>

#include <functional>

#include "nocopy.hpp"

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

54

55

56

57

58

#include "Log.hpp"

#include "Comm.hpp"

#include "InetAddr.hpp"

const static uint16_t defaultport = 8888;

const static int defaultfd = -1;

const static int defaultsize = 1024;

using func_t = std::function<void(const std::string &req, std::string *resp)>;

class UdpServer : public nocopy

{

public:

    UdpServer(func_t func, uint16_t port = defaultport)

        : _func(func),_port(port),_sockfd(defaultfd)

    {

    }

    void Init()

    {
        // 1. 创建socket，就是创建了⽂件细节
        _sockfd = socket(AF_INET, SOCK_DGRAM, 0);

        if (_sockfd < 0)

        {

            lg.LogMessage(Fatal, "socket errr, %d : %s\n", errno,

strerror(errno));

            exit(Socket_Err);

        }

        lg.LogMessage(Info, "socket success, sockfd: %d\n", _sockfd);

        // 2. 绑定，指定⽹络信息
        struct sockaddr_in local;

        bzero(&local, sizeof(local)); // memset

        local.sin_family = AF_INET;

        local.sin_port = htons(_port);

        local.sin_addr.s_addr = INADDR_ANY; // 0

        // local.sin_addr.s_addr = inet_addr(_ip.c_str()); // 1. 4字节IP 2. 变
成⽹络序列

        // 结构体填完，设置到内核中了吗？？没有
        int n = ::bind(_sockfd, (struct sockaddr *)&local, sizeof(local));

        if (n != 0)

        {

            lg.LogMessage(Fatal, "bind errr, %d : %s\n", errno,

strerror(errno));

59

            exit(Bind_Err);

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

76

77

78

79

80

81

82

83

84

85

86

87

88

89

90

91

        }

    }

    void Start()

    {
        // 服务器永远不退出
        char buffer[defaultsize];

        for (;;)

        {

            struct sockaddr_in peer;
            socklen_t len = sizeof(peer); // 不能乱写
            ssize_t n = recvfrom(_sockfd, buffer, sizeof(buffer) - 1, 0,

(struct sockaddr *)&peer, &len);

            if (n > 0)

            {

                InetAddr addr(peer);

                buffer[n] = 0;

                std::cout << "[" << addr.PrintDebug() << "]# " << buffer <<

std::endl;

                std::string value;
                _func(buffer, &value); // 回调业务翻译⽅法
                sendto(_sockfd, value.c_str(), value.size(), 0, (struct

sockaddr *)&peer, len);

            }

        }

    }

    ~UdpServer()

    {

    }

private:
    // std::string _ip; // 后⾯要调整
    uint16_t _port;

    int _sockfd;

    func_t _func;

};

Main.cc

1

2

3

4

5

6

7

#include "UdpServer.hpp"

#include "Comm.hpp"

#include "Dict.hpp"

#include <memory>

void Usage(std::string proc)

{

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

    std::cout << "Usage : \n\t" << proc << " local_port\n" << std::endl;

}

Dict gdict("./dict.txt");

void Execute(const std::string &req, std::string *resp)

{

    *resp = gdict.Translate(req);

}

// ./udp_server 8888

int main(int argc, char *argv[])

{

    if(argc != 2)

    {

        Usage(argv[0]);

        return Usage_Err;

    }

    // std::string ip = argv[1];

    uint16_t port = std::stoi(argv[1]);
    //Lambda写法
    //Dict gdict("./dict.txt");

    //std::unique_ptr<UdpServer> usvr = std::make_unique<UdpServer>(port,

[&gdict](const std::string &message)->std::string{

    //    return gdict.Translate(message);

    //});

    std::unique_ptr<UdpServer> usvr = std::make_unique<UdpServer>(Execute,

port);

    usvr->Init();

    usvr->Start();

    return 0;

}

V2版本-DictServer封装版

下⾯是⼀个封装版的，⼤家下来可以看⼀下

udp_socket.hpp

#pragma once

#include <stdio.h>

#include <string.h>

#include <stdlib.h>

#include <cassert>

#include <string>

#include <unistd.h>

#include <sys/socket.h>

#include <netinet/in.h>

#include <arpa/inet.h>

typedef struct sockaddr sockaddr;

typedef struct sockaddr_in sockaddr_in;

class UdpSocket {

public:

  UdpSocket() : fd_(-1) {

  }

  bool Socket() {

    fd_ = socket(AF_INET, SOCK_DGRAM, 0);

    if (fd_ < 0) {

      perror("socket");

      return false;

    }

    return true;

  }

  bool Close() {

    close(fd_);

    return true;

  }

  bool Bind(const std::string& ip, uint16_t port) {

    sockaddr_in addr;

    addr.sin_family = AF_INET;

    addr.sin_addr.s_addr = inet_addr(ip.c_str());

    addr.sin_port = htons(port);

    int ret = bind(fd_, (sockaddr*)&addr, sizeof(addr));

    if (ret < 0) {

      perror("bind");

      return false;

    }

    return true;

  }

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

  bool RecvFrom(std::string* buf, std::string* ip = NULL, uint16_t* port =

NULL) {

    char tmp[1024 * 10] = {0};

    sockaddr_in peer;

    socklen_t len = sizeof(peer);

    ssize_t read_size = recvfrom(fd_, tmp,

                                  sizeof(tmp) - 1, 0, (sockaddr*)&peer, &len);

    if (read_size < 0) {

      perror("recvfrom");

      return false;

    }
    // 将读到的缓冲区内容放到输出参数中
    buf->assign(tmp, read_size);

    if (ip != NULL) {

      *ip = inet_ntoa(peer.sin_addr);

    }

    if (port != NULL) {

      *port = ntohs(peer.sin_port);

    }

    return true;

  }

  bool SendTo(const std::string& buf, const std::string& ip, uint16_t port) {

    sockaddr_in addr;

    addr.sin_family = AF_INET;

    addr.sin_addr.s_addr = inet_addr(ip.c_str());

    addr.sin_port = htons(port);

    ssize_t write_size = sendto(fd_, buf.data(), buf.size(), 0,

(sockaddr*)&addr, sizeof(addr));

    if (write_size < 0) {

      perror("sendto");

      return false;

    }

    return true;

  }

private:

  int fd_;

};

48

49

50

51

52

53

54

55

56

57

58

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

76

77

78

79

80

81

82

83

UDP通⽤服务器

udp_server.hpp

1

2

#pragma once

#include "udp_socket.hpp"

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

// C 式写法
// typedef void (*Handler)(const std::string& req, std::string* resp);
// C++ 11 式写法, 能够兼容函数指针, 仿函数, 和 lambda
#include <functional>

typedef std::function<void (const std::string&, std::string* resp)> Handler;

class UdpServer {

public:

  UdpServer() {

    assert(sock_.Socket());

  }

  ~UdpServer() {

    sock_.Close();

  }

  bool Start(const std::string& ip, uint16_t port, Handler handler) {
    // 1. 创建 socket
    // 2. 绑定端⼝号
    bool ret = sock_.Bind(ip, port);

    if (!ret) {

      return false;

    }
    // 3. 进⼊事件循环
    for (;;) {
      // 4. 尝试读取请求
      std::string req;

      std::string remote_ip;

      uint16_t remote_port = 0;

      bool ret = sock_.RecvFrom(&req, &remote_ip, &remote_port);

      if (!ret) {

        continue;

      }

      std::string resp;
      // 5. 根据请求计算响应
      handler(req, &resp);
      // 6. 返回响应给客⼾端
      sock_.SendTo(resp, remote_ip, remote_port);

      printf("[%s:%d] req: %s, resp: %s\n", remote_ip.c_str(), remote_port,

            req.c_str(), resp.c_str());

    }

    sock_.Close();

    return true;

  }

private:

50

51

  UdpSocket sock_;

};

实现英译汉服务器

以上代码是对udp服务器进⾏通⽤接⼝的封装.基于以上封装,实现⼀个查字典的服务器就很容易了.

dict_server.cc

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

#include "udp_server.hpp"

#include <unordered_map>

#include <iostream>

std::unordered_map<std::string, std::string> g_dict;

void Translate(const std::string& req, std::string* resp) {

  auto it = g_dict.find(req);

  if (it == g_dict.end()) {
    *resp = "未查到!";
    return;

  }

  *resp = it->second;

}

int main(int argc, char* argv[]) {

  if (argc != 3) {

    printf("Usage ./dict_server [ip] [port]\n");

    return 1;

  }
  // 1. 数据初始化
  g_dict.insert(std::make_pair("hello", "你好"));
  g_dict.insert(std::make_pair("world", "世界"));
  g_dict.insert(std::make_pair("c++", "最好的编程语⾔"));
  g_dict.insert(std::make_pair("bit", "特别NB"));
  // 2. 启动服务器
  UdpServer server;

  server.Start(argv[1], atoi(argv[2]), Translate);

  return 0;

}

UDP通⽤客⼾端

udp_client.hpp

1

#pragma once

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

#include "udp_socket.hpp"

class UdpClient {

public:

  UdpClient(const std::string& ip, uint16_t port) : ip_(ip), port_(port) {

    assert(sock_.Socket());

  }

  ~UdpClient() {

    sock_.Close();

  }

  bool RecvFrom(std::string* buf) {

    return sock_.RecvFrom(buf);

  }

  bool SendTo(const std::string& buf) {

    return sock_.SendTo(buf, ip_, port_);

  }

private:

  UdpSocket sock_;
  // 服务器端的 IP 和 端⼝号
  std::string ip_;

  uint16_t port_;

};

实现英译汉客⼾端

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

#include "udp_client.hpp"

#include <iostream>

int main(int argc, char* argv[]) {

  if (argc != 3) {

    printf("Usage ./dict_client [ip] [port]\n");

    return 1;

  }

  UdpClient client(argv[1], atoi(argv[2]));

  for (;;) {

    std::string word;
    std::cout << "请输⼊您要查的单词: ";
    std::cin >> word;

    if (!std::cin) {

      std::cout << "Good Bye" << std::endl;

      break;

    }

18

19

20

21

22

23

24

    client.SendTo(word);

    std::string result;

    client.RecvFrom(&result);
    std::cout << word << " 意思是 " << result << std::endl;
  }

  return 0;

}

V3版本-简单聊天室

Route.hpp

代码块

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

#pragma once

#include <iostream>

#include <string>

#include <vector>

#include "InetAddr.hpp"

#include "Log.hpp"

using namespace LogModule;

class Route

{

private:

    bool IsExist(InetAddr &peer)

    {

        for (auto &user : _online_user)

        {

            if (user == peer)

            {

                return true;

            }

        }

        return false;

    }

    void AddUser(InetAddr &peer)

    {
        LOG(LogLevel::INFO) << "新增⼀个在线⽤⼾: " << peer.StringAddr();
        _online_user.push_back(peer);

    }

    void DeleteUser(InetAddr &peer)

    {

        for (auto iter = _online_user.begin(); iter != _online_user.end();

iter++)

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

53

54

55

56

57

58

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

        {

            if (*iter == peer)

            {
                LOG(LogLevel::INFO) << "删除⼀个在线⽤⼾:" << peer.StringAddr()
<< "成功";
                _online_user.erase(iter);

                break;

            }

        }

    }

public:

    Route()

    {

    }

    void MessageRoute(int sockfd, const std::string &message, InetAddr &peer)

    {

        if (!IsExist(peer))

        {

            AddUser(peer);

        }

        std::string send_message = peer.StringAddr() + "# " + message; //
127.0.0.1:8080# 你好

        // TODO

        for (auto &user : _online_user)

        {

            sendto(sockfd, send_message.c_str(), send_message.size(), 0, (const

 struct sockaddr *)&(user.NetAddr()), sizeof(user.NetAddr()));

        }

        // 这个⽤⼾⼀定已经在线了
        if (message == "QUIT")

        {
            LOG(LogLevel::INFO) << "删除⼀个在线⽤⼾: " << peer.StringAddr();
            DeleteUser(peer);

        }

    }

    ~Route()

    {

    }

private:
    // ⾸次给我发消息，等同于登录
    std::vector<InetAddr> _online_user; // 在线⽤⼾
};

UdpServer.hpp

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

#pragma once

#include <iostream>

#include <string>

#include <functional>

#include <strings.h>

#include <sys/types.h>

#include <sys/socket.h>

#include <netinet/in.h>

#include <arpa/inet.h>

#include "Log.hpp"

#include "InetAddr.hpp"

using namespace LogModule;

using func_t = std::function<void(int sockfd, const std::string&, InetAddr&)>;

const int defaultfd = -1;

// 你是为了进⾏⽹络通信的！
class UdpServer

{

public:

    UdpServer(uint16_t port, func_t func)

        : _sockfd(defaultfd),

        //   _ip(ip),

          _port(port),

          _isrunning(false),

          _func(func)

    {

    }

    void Init()

    {
        // 1. 创建套接字
        _sockfd = socket(AF_INET, SOCK_DGRAM, 0);

        if (_sockfd < 0)

        {

            LOG(LogLevel::FATAL) << "socket error!";

            exit(1);

        }

        LOG(LogLevel::INFO) << "socket success, sockfd : " << _sockfd;

        // 2. 绑定socket信息，ip和端⼝， ip(⽐较特殊，后续解释)

44

45

46

47

48

49

50

51

52

53

54

55

56

57

58

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

76

77

78

79

80

81

82

83

84

85

86

        // 2.1 填充sockaddr_in结构体
        struct sockaddr_in local;

        bzero(&local, sizeof(local));

        local.sin_family = AF_INET;
        // 我会不会把我的IP地址和端⼝号发送给对⽅？
        // IP信息和端⼝信息，⼀定要发送到⽹络！
        // 本地格式->⽹络序列
        local.sin_port = htons(_port);
        // IP也是如此，1. IP转成4字节 2. 4字节转成⽹络序列 -> in_addr_t
inet_addr(const char *cp);

        //local.sin_addr.s_addr = inet_addr(_ip.c_str()); // TODO

        local.sin_addr.s_addr = INADDR_ANY;

        // 那么为什么服务器端要显式的bind呢？IP和端⼝必须是众所周知且不能轻易改变的！
        int n = bind(_sockfd, (struct sockaddr *)&local, sizeof(local));

        if (n < 0)

        {

            LOG(LogLevel::FATAL) << "bind error";

            exit(2);

        }

        LOG(LogLevel::INFO) << "bind success, sockfd : " << _sockfd;

    }

    void Start()

    {

        _isrunning = true;

        while (_isrunning)

        {

            char buffer[1024];

            struct sockaddr_in peer;

            socklen_t len = sizeof(peer);
            // 1. 收消息, client为什么要个服务器发送消息啊？不就是让服务端处理数据。
            ssize_t s = recvfrom(_sockfd, buffer, sizeof(buffer) - 1, 0,

(struct sockaddr *)&peer, &len);

            if (s > 0)

            {

                InetAddr client(peer);

                buffer[s] = 0;

                // TODO

                _func(_sockfd, buffer, client);

                // LOG(LogLevel::DEBUG) << "[" << peer_ip << ":" <<
peer_port<< "]# " << buffer; // 1. 消息内容 2. 谁发的？？

                // 2. 发消息
                // std::string echo_string = "server echo@ ";

                // echo_string += buffer;

87

                // sendto(_sockfd, result.c_str(), result.size(), 0, (struct

sockaddr*)&peer, len);

            }

        }

    }

    ~UdpServer()

    {

    }

private:

    int _sockfd;

    uint16_t _port;
    // std::string _ip; // ⽤的是字符串⻛格，点分⼗进制, "192.168.1.1"
    bool _isrunning;

    func_t _func; // 服务器的回调函数，⽤来进⾏对数据进⾏处理
};

88

89

90

91

92

93

94

95

96

97

98

99

100

101

102

• 引⼊线程池，这⾥就不重复贴代码了

InetAddr.hpp

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

#pragma once

#include <iostream>

#include <string>

#include <sys/types.h>

#include <sys/socket.h>

#include <netinet/in.h>

#include <arpa/inet.h>

class InetAddr

{

public:

    InetAddr(struct sockaddr_in &addr):_addr(addr)

    {

        _port = ntohs(_addr.sin_port);

        _ip = inet_ntoa(_addr.sin_addr);

    }

    std::string Ip() {return _ip;}

    uint16_t Port() {return _port;};

    std::string PrintDebug()

    {

        std::string info = _ip;

        info += ":";

        info += std::to_string(_port);  // "127.0.0.1:4444"

        return info;

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

    }

    const  struct sockaddr_in& GetAddr()

    {

        return _addr;

    }

    bool operator == (const InetAddr&addr)

    {

        //other code

        return this->_ip == addr._ip && this->_port == addr._port;

    }

    ~InetAddr(){}

private:

    std::string _ip;

    uint16_t _port;

    struct sockaddr_in _addr;

};

• 在InetAddr中，重载⼀下 == ⽅便对⽤⼾是否是同⼀个进⾏⽐较

ServerMain.cc

代码块

1

2

3

4

5

6

7

8

9

10

11

12

13

14

    // 单进程服务器
    // std::unique_ptr<UdpServer> usvr = std::make_unique<UdpServer>(port, [&r]

(int sockfd, const std::string &message, InetAddr&peer){

    //     r.MessageRoute(sockfd, message, peer);

    // });

    //进程池服务器
    // 1. 路由服务
    std::unique_ptr<Route> r = std::make_unique<Route>();

    // 2. 线程池
    auto tp = ThreadPool<task_t>::GetInstance();

    // 3. ⽹络服务器对象，提供通信功能
    std::unique_ptr<UdpServer> usvr = std::make_unique<UdpServer>(port, [&r,

&tp](int sockfd, const std::string &message, InetAddr&peer){

15

        task_t t = std::bind(&Route::MessageRoute, r.get(), sockfd, message,

peer);

16

17

        tp->Enqueue(t);

    });

UdpClient.hpp

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

#include <iostream>

#include <cerrno>

#include <cstring>

#include <string>

#include <unistd.h>

#include <sys/types.h> /* See NOTES */

#include <sys/socket.h>

#include <arpa/inet.h>

#include <netinet/in.h>

#include "Thread.hpp"

#include "InetAddr.hpp"

void Usage(const std::string &process)

{

    std::cout << "Usage: " << process << " server_ip server_port" <<

std::endl;

}

class ThreadData

{

public:

    ThreadData(int sock, struct sockaddr_in &server) : _sockfd(sock),

_serveraddr(server)

    {

    }

    ~ThreadData()

    {

    }

public:

    int _sockfd;

    InetAddr _serveraddr;

};

void RecverRoutine(ThreadData &td)

{

    char buffer[4096];

    while (true)

    {

        struct sockaddr_in temp;

        socklen_t len = sizeof(temp);

        ssize_t n = recvfrom(td._sockfd, buffer, sizeof(buffer) - 1, 0,
(struct sockaddr *)&temp, &len); // ⼀般建议都是要填的.
        if (n > 0)

        {

            buffer[n] = 0;
            std::cerr << buffer << std::endl; // ⽅便⼀会查看效果

        }

        else

            break;

    }

}

// 该线程只负责发消息
void SenderRoutine(ThreadData &td)

{

    while (true)

    {
        // 我们要发的数据
        std::string inbuffer;

        std::cout << "Please Enter# ";

        std::getline(std::cin, inbuffer);

        auto server = td._serveraddr.GetAddr();
        // 我们要发给谁呀？server
        ssize_t n = sendto(td._sockfd, inbuffer.c_str(), inbuffer.size(), 0,

(struct sockaddr *)&server, sizeof(server));

        if (n <= 0)

            std::cout << "send error" << std::endl;

    }

}

// ./udp_client server_ip server_port

int main(int argc, char *argv[])

{

    if (argc != 3)

    {

        Usage(argv[0]);

        return 1;

    }

    std::string serverip = argv[1];

    uint16_t serverport = std::stoi(argv[2]);

    // 1. 创建socket
    // udp是全双⼯的。既可以读，也可以写，可以同时读写，不会多线程读写的问题
    int sock = socket(AF_INET, SOCK_DGRAM, 0);

    if (sock < 0)

    {

        std::cerr << "socket error: " << strerror(errno) << std::endl;

        return 2;

    }

    std::cout << "create socket success: " << sock << std::endl;

45

46

47

48

49

50

51

52

53

54

55

56

57

58

59

60

61

62

63

64

65

66

67

68

69

70

71

72

73

74

75

76

77

78

79

80

81

82

83

84

85

86

87

88

89

90

91

92

93

94

95

96

97

98

99

100

101

102

103

104

105

106

107

108

109

110

111

112

113

    // 2. client要不要进⾏bind? ⼀定要bind的！！但是，不需要显⽰bind，client会在⾸次
发送数据的时候会⾃动进⾏bind
    // 为什么？server端的端⼝号，⼀定是众所周知，不可改变的，client 需要 port，bind随
机端⼝.
    // 为什么？client会⾮常多.
    // client 需要bind，但是不需要显⽰bind，让本地OS⾃动随机bind，选择随机端⼝号
    // 2.1 填充⼀下server信息
    struct sockaddr_in server;

    memset(&server, 0, sizeof(server));

    server.sin_family = AF_INET;

    server.sin_port = htons(serverport);

    server.sin_addr.s_addr = inet_addr(serverip.c_str());

    ThreadData td(sock, server);

    Thread<ThreadData> recver("recver", RecverRoutine, td);

    Thread<ThreadData> sender("sender", SenderRoutine, td);

    recver.Start();

    sender.Start();

    recver.Join();

    sender.Join();

    close(sock);

    return 0;

}

• UDP协议⽀持全双⼯，⼀个sockfd，既可以读取，⼜可以写⼊，对于客⼾端和服务端同样如此

• 多线程客⼾端，同时读取和写⼊

• 测试的时候，使⽤管道进⾏演⽰

补充参考内容

地址转换函数

本节只介绍基于IPv4的socket⽹络编程,sockaddr_in中的成员structin_addrsin_addr表⽰32位的IP

地址

但是我们通常⽤点分⼗进制的字符串表⽰IP地址,以下函数可以在字符串表⽰和in_addr表⽰之间转换;

字符串转in_addr的函数:

in_addr转字符串的函数:

其中inet_pton和inet_ntop不仅可以转换IPv4的in_addr,还可以转换IPv6的in6_addr,因此函数接⼝是

void*addrptr。

代码⽰例:

关于inet_ntoa

inet_ntoa这个函数返回了⼀个char*,很显然是这个函数⾃⼰在内部为我们申请了⼀块内存来保存ip的

结果.那么是否需要调⽤者⼿动释放呢?

man⼿册上说,inet_ntoa函数,是把这个返回结果放到了静态存储区.这个时候不需要我们⼿动进⾏释

放.

那么问题来了,如果我们调⽤多次这个函数,会有什么样的效果呢?参⻅如下代码:

运⾏结果如下:

因为inet_ntoa把结果放到⾃⼰内部的⼀个静态存储区,这样第⼆次调⽤时的结果会覆盖掉上⼀次的结

果.

• 思考:如果有多个线程调⽤inet_ntoa,是否会出现异常情况呢?

• 在APUE中,明确提出inet_ntoa不是线程安全的函数;

• 但是在centos7上测试,并没有出现问题,可能内部的实现加了互斥锁;

• 同学们课后⾃⼰写程序验证⼀下在⾃⼰的机器上inet_ntoa是否会出现多线程的问题;

• 在多线程环境下,推荐使⽤inet_ntop,这个函数由调⽤者提供⼀个缓冲区保存结果,可以规避线程

安全问题;

多线程调⽤inet_ntoa代码⽰例如下(同学们课后⾃⼰测试):

#include <stdio.h>

#include <unistd.h>

#include <sys/socket.h>

#include <netinet/in.h>

#include <arpa/inet.h>

#include <pthread.h>

void* Func1(void* p) {

  struct sockaddr_in* addr = (struct sockaddr_in*)p;

  while (1) {

    char* ptr = inet_ntoa(addr->sin_addr);

    printf("addr1: %s\n", ptr);

  }

  return NULL;

}

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

void* Func2(void* p) {

  struct sockaddr_in* addr = (struct sockaddr_in*)p;

  while (1) {

    char* ptr = inet_ntoa(addr->sin_addr);

    printf("addr2: %s\n", ptr);

  }

  return NULL;

}

int main() {

  pthread_t tid1 = 0;

  struct sockaddr_in addr1;

  struct sockaddr_in addr2;

  addr1.sin_addr.s_addr = 0;

  addr2.sin_addr.s_addr = 0xffffffff;

  pthread_create(&tid1, NULL, Func1, &addr1);

  pthread_t tid2 = 0;

  pthread_create(&tid2, NULL, Func2, &addr2);

  pthread_join(tid1, NULL);

  pthread_join(tid2, NULL);

  return 0;

}

remove_if 样例

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

#include <iostream>

#include <list>

#include <memory>

#include <algorithm>

int main()

{

    std::list<std::shared_ptr<int> > ls;

    ls.push_back(std::make_shared<int>(1));

    ls.push_back(std::make_shared<int>(2));

    ls.push_back(std::make_shared<int>(3));

    ls.push_back(std::make_shared<int>(4));

    ls.push_back(std::make_shared<int>(4));

    ls.push_back(std::make_shared<int>(4));

    ls.push_back(std::make_shared<int>(5));

    ls.push_back(std::make_shared<int>(6));

    for(auto &v : ls)

    {

        std::cout << *v <<std::endl;

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

    }

    std::cout << "aa: " <<ls.size() <<std::endl;

    std::cout << "\n";

    //int a = 3;

    int a = 4;

    auto pos = remove_if(ls.begin(), ls.end(), [&a](const

std::shared_ptr<int> &elem)->bool{

                  return a == *elem;

              });

    ls.erase(pos, ls.end());

    std::cout << "aa: " <<ls.size() <<std::endl;

    for(auto &v : ls)

    {

        std::cout << *v <<std::endl;

    }

    return 0;

}

//remove_if()并不会实际移除序列[start, end)中的元素; 如果在⼀个容器上应⽤
remove_if(), 容器的⻓度并不会改变, 所有的元素都还在容器⾥⾯（但是逻辑上已经⽆法访问）.
remove_if()将所有应该移除的元素都移动到容器尾部并返回⼀个分界的迭代器. 为了实际移除元
素, 你必须对容器⾃⾏调⽤erase()以擦除需要移除的元素

