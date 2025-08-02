# test_stdio_client.py
import subprocess
import json
import sys
import time

def send_message(process, message, expect_response=True):
    """MCP 서버에 메시지를 보내고 응답을 받습니다."""
    print(f"전송: {json.dumps(message)}")
    process.stdin.write(json.dumps(message) + "\n")
    process.stdin.flush()
    
    # 알림 메시지는 응답이 없을 수 있음
    if not expect_response:
        print("알림 메시지 전송 완료 (응답 대기 안함)")
        time.sleep(0.5)  # 잠시 대기
        return None
    
    # 응답 읽기
    try:
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"응답: {json.dumps(response, ensure_ascii=False, indent=2)}")
            return response
        else:
            print("응답 없음")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류: {e}")
        print(f"원본 응답: {response_line}")
        return None

def test_mcp_stdio():
    """MCP STDIO 서버를 테스트합니다."""
    
    # MCP 서버 프로세스 시작
    print("MCP 서버 시작 중...")
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # 라인 버퍼링
    )
    
    try:
        # 서버 시작 대기
        time.sleep(2)
        
        print("\n=== 1. 초기화 요청 ===")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        init_response = send_message(process, init_request)
        
        print("\n=== 2. 초기화 완료 알림 ===")
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        send_message(process, initialized_notification, expect_response=False)
        
        print("\n=== 3. 도구 목록 요청 ===")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        tools_response = send_message(process, tools_request)
        
        print("\n=== 4. 헬스 체크 도구 호출 ===")
        health_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "health_check",
                "arguments": {}
            }
        }
        
        health_response = send_message(process, health_request)
        
        print("\n=== 5. 분석 도구 호출 ===")
        analyze_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "analyze_and_plot",
                "arguments": {
                    "keyword": "machine learning"
                }
            }
        }
        
        analyze_response = send_message(process, analyze_request)
        
        print("\n=== 테스트 완료 ===")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        
        # stderr 출력 확인
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"서버 에러 출력: {stderr_output}")
            
    finally:
        # 프로세스 종료
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_mcp_stdio()