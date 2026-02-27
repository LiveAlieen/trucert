#!/usr/bin/env python3
"""
证书管理系统 Web 应用
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(parent_dir)
sys.path.insert(0, project_root)

from trucert.core.services import (
    KeyService, CertService, FileSignerService, 
    VerifierService, ConfigService
)
from trucert.core.utils import initialize_dependencies

# 初始化依赖注入容器
initialize_dependencies()

app = Flask(__name__)

# 初始化服务
key_service = KeyService()
cert_service = CertService()
file_signer_service = FileSignerService()
verifier_service = VerifierService()
config_service = ConfigService()

# 获取算法配置
algorithms = config_service.get_algorithms()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', algorithms=algorithms.get('data', {}))

@app.route('/api/keys', methods=['GET'])
def list_keys():
    """列出所有密钥"""
    result = key_service.list_keys()
    if result.get("success"):
        return jsonify({"success": True, "keys": result["data"]})
    return jsonify({"success": False, "error": result.get("error", "未知错误")})

@app.route('/api/keys', methods=['POST'])
def generate_key():
    """生成密钥对"""
    data = request.json
    key_type = data.get('type', 'RSA')
    
    if key_type == 'RSA':
        key_size = data.get('key_size', 2048)
        result = key_service.generate_rsa_key({"key_size": key_size})
    else:
        curve = data.get('curve', 'SECP256R1')
        result = key_service.generate_ecc_key({"curve": curve})
    
    if result.get("success"):
        return jsonify({"success": True, "data": result["data"]})
    return jsonify({"success": False, "error": result.get("error", "未知错误")})

@app.route('/api/keys/<key_id>', methods=['DELETE'])
def delete_key(key_id):
    """删除密钥"""
    result = key_service.delete_key({"key_id": key_id})
    if result.get("success"):
        return jsonify({"success": True})
    return jsonify({"success": False, "error": result.get("error", "未知错误")})

@app.route('/api/certs', methods=['GET'])
def list_certs():
    """列出所有证书"""
    result = cert_service.list_certs()
    if result.get("success"):
        return jsonify({"success": True, "certs": result["data"]})
    return jsonify({"success": False, "error": result.get("error", "未知错误")})

@app.route('/api/certs/self-signed', methods=['POST'])
def generate_self_signed_cert():
    """生成自签名证书"""
    data = request.json
    
    try:
        # 加载密钥
        key_id = data.get('key_id')
        if not key_id:
            return jsonify({"success": False, "error": "请选择密钥"})
        
        result_load = key_service.load_key_pair({"key_id": key_id})
        if not result_load.get("success"):
            return jsonify({"success": False, "error": result_load.get("error", "加载密钥失败")})
        
        private_key = result_load["data"]["private_key"]
        public_key = result_load["data"]["public_key"]
        
        validity_days = data.get('validity_days', 365)
        forward_offset = data.get('forward_offset', 0)
        
        result_cert = cert_service.generate_self_signed_cert({
            "public_key": public_key,
            "private_key": private_key,
            "validity_days": validity_days,
            "forward_offset": forward_offset
        })
        
        if result_cert.get("success"):
            return jsonify({"success": True, "data": result_cert["data"]})
        return jsonify({"success": False, "error": result_cert.get("error", "未知错误")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/certs/<cert_id>', methods=['DELETE'])
def delete_cert(cert_id):
    """删除证书"""
    result = cert_service.delete_cert({"filepath": cert_id})
    if result.get("success"):
        return jsonify({"success": True})
    return jsonify({"success": False, "error": result.get("error", "未知错误")})

@app.route('/api/sign/file', methods=['POST'])
def sign_file():
    """签名文件"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "请选择文件"})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "请选择文件"})
        
        key_id = request.form.get('key_id')
        if not key_id:
            return jsonify({"success": False, "error": "请选择密钥"})
        
        hash_algorithm = request.form.get('hash_algorithm', 'sha256')
        
        # 保存上传的文件
        import tempfile
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 加载密钥
        result_load = key_service.load_key_pair({"key_id": key_id})
        if not result_load.get("success"):
            return jsonify({"success": False, "error": result_load.get("error", "加载密钥失败")})
        
        private_key = result_load["data"]["private_key"]
        
        # 签名文件
        result_sign = file_signer_service.sign_file({
            "file_path": file_path,
            "private_key": private_key,
            "hash_algorithm": hash_algorithm
        })
        
        if result_sign.get("success"):
            signature = result_sign["data"]
            
            # 保存签名
            import json
            sig_data = {
                "signature": signature.hex(),
                "original_file_path": file.filename,
                "hash_algorithm": hash_algorithm,
                "file_size": file_size,
                "file_info": {
                    "filename": file.filename,
                    "file_size": file_size
                }
            }
            
            sig_filename = file.filename + ".giq"
            
            # 清理临时文件
            import shutil
            shutil.rmtree(temp_dir)
            
            return jsonify({
                "success": True, 
                "signature": sig_data,
                "filename": sig_filename
            })
        
        return jsonify({"success": False, "error": result_sign.get("error", "签名失败")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/sign/batch', methods=['POST'])
def batch_sign_files():
    """批量签名文件"""
    try:
        if 'files' not in request.files:
            return jsonify({"success": False, "error": "请选择文件"})
        
        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return jsonify({"success": False, "error": "请选择文件"})
        
        key_id = request.form.get('key_id')
        if not key_id:
            return jsonify({"success": False, "error": "请选择密钥"})
        
        hash_algorithm = request.form.get('hash_algorithm', 'sha256')
        
        # 保存上传的文件
        import tempfile
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        
        for file in files:
            if file.filename:
                file_path = os.path.join(temp_dir, file.filename)
                file.save(file_path)
                file_paths.append(file_path)
        
        # 加载密钥
        result_load = key_service.load_key_pair({"key_id": key_id})
        if not result_load.get("success"):
            return jsonify({"success": False, "error": result_load.get("error", "加载密钥失败")})
        
        private_key = result_load["data"]["private_key"]
        
        # 批量签名文件
        import uuid
        import datetime
        timestamp = int(datetime.datetime.now().timestamp())
        unique_id = str(uuid.uuid4())[:8]
        sig_filename = f"batch_sign_{timestamp}_{unique_id}.giqs"
        
        # 调用批量签名服务（使用临时目录作为输出目录）
        result_batch = file_signer_service.batch_sign({
            "filepaths": file_paths,
            "private_key": private_key,
            "output_dir": temp_dir,
            "hash_algorithm": hash_algorithm
        })
        
        if result_batch.get("success"):
            # 读取生成的批量签名文件
            batch_sig_path = os.path.join(temp_dir, sig_filename)
            import json
            with open(batch_sig_path, 'r', encoding='utf-8') as f:
                batch_sig_data = json.load(f)
            
            # 清理临时文件
            import shutil
            shutil.rmtree(temp_dir)
            
            return jsonify({
                "success": True, 
                "signature": batch_sig_data,
                "filename": sig_filename,
                "total_files": len(file_paths),
                "successful_files": len([r for r in result_batch["data"] if r["success"]])
            })
        
        return jsonify({"success": False, "error": result_batch.get("error", "批量签名失败")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/verify/file', methods=['POST'])
def verify_file():
    """验证文件签名"""
    try:
        if 'file' not in request.files or 'signature' not in request.files:
            return jsonify({"success": False, "error": "请选择文件和签名"})
        
        file = request.files['file']
        signature_file = request.files['signature']
        verify_method = request.form.get('verify_method', 'key')  # 'key' 或 'cert'
        key_id = request.form.get('key_id')
        cert_id = request.form.get('cert_id')
        
        if file.filename == '' or signature_file.filename == '':
            return jsonify({"success": False, "error": "请选择文件和签名"})
        
        # 保存上传的文件
        import tempfile
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        sig_path = os.path.join(temp_dir, signature_file.filename)
        file.save(file_path)
        signature_file.save(sig_path)
        
        # 加载签名
        result_sig = file_signer_service.load_signature({"file_path": sig_path})
        if not result_sig.get("success"):
            return jsonify({"success": False, "error": result_sig.get("error", "加载签名失败")})
        
        signature_data = result_sig["data"]
        signature = signature_data["signature"]
        hash_algorithm = signature_data["hash_algorithm"]
        
        # 根据验证方式选择不同的验证方法
        if verify_method == 'key':
            # 使用公钥验证
            if not key_id:
                return jsonify({"success": False, "error": "请选择密钥"})
            
            # 加载公钥
            result_load = key_service.load_key_pair({"key_id": key_id})
            if not result_load.get("success"):
                return jsonify({"success": False, "error": result_load.get("error", "加载密钥失败")})
            
            public_key = result_load["data"]["public_key"]
            
            # 验证签名
            result_verify = file_signer_service.verify_file_signature({
                "file_path": file_path,
                "signature": signature,
                "public_key": public_key,
                "hash_algorithm": hash_algorithm
            })
        else:
            # 使用证书验证
            if not cert_id:
                return jsonify({"success": False, "error": "请选择证书"})
            
            # 加载证书
            result_cert = cert_service.load_cert({"filepath": cert_id})
            if not result_cert.get("success"):
                return jsonify({"success": False, "error": result_cert.get("error", "加载证书失败")})
            
            cert_data = result_cert["data"]
            
            # 保存证书到临时文件
            import json
            cert_path = os.path.join(temp_dir, f"temp_cert_{cert_id}.tru")
            with open(cert_path, 'w', encoding='utf-8') as f:
                json.dump(cert_data, f, indent=2, ensure_ascii=False)
            
            # 验证签名
            result_verify = file_signer_service.verify_file_signature_with_cert({
                "file_path": file_path,
                "signature": signature,
                "certificate": cert_path,
                "hash_algorithm": hash_algorithm
            })
        
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)
        
        if result_verify.get("success"):
            return jsonify({"success": True, "valid": result_verify["data"]})
        
        return jsonify({"success": False, "error": result_verify.get("error", "验证失败")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/static/<path:path>')
def serve_static(path):
    """提供静态文件"""
    return send_from_directory('static', path)

if __name__ == '__main__':
    print("启动证书管理系统 Web 应用...")
    print("访问地址: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
