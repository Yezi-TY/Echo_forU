import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const filePath = searchParams.get('path');

  if (!filePath) {
    return NextResponse.json({ error: 'File path is required' }, { status: 400 });
  }

  // 安全检查：确保路径在 Build/outputs 目录下
  // 如果传入的是绝对路径，提取文件名；如果是相对路径，直接使用
  let fileName: string;
  if (path.isAbsolute(filePath)) {
    fileName = path.basename(filePath);
  } else {
    fileName = path.basename(filePath);
  }

  // 构建完整的文件路径
  // Next.js 在开发模式下，process.cwd() 是 frontend/web 目录
  // 需要向上两级到达项目根目录
  const projectRoot = path.resolve(process.cwd(), '..', '..');
  const outputsDir = path.join(projectRoot, 'Build', 'outputs');
  const fullPath = path.join(outputsDir, fileName);

  // 验证文件是否在允许的目录内
  const resolvedOutputsDir = path.resolve(outputsDir);
  const resolvedFullPath = path.resolve(fullPath);
  if (!resolvedFullPath.startsWith(resolvedOutputsDir)) {
    return NextResponse.json({ error: 'Invalid file path' }, { status: 403 });
  }

  try {
    // 检查文件是否存在
    if (!fs.existsSync(fullPath)) {
      return NextResponse.json({ error: 'File not found', details: { fullPath, fileName } }, { status: 404 });
    }

    // 读取文件
    const fileBuffer = fs.readFileSync(fullPath);
    const stats = fs.statSync(fullPath);

    // 根据文件扩展名确定 Content-Type
    const ext = path.extname(fileName).toLowerCase();
    let contentType = 'audio/mpeg'; // 默认 MP3
    if (ext === '.wav') {
      contentType = 'audio/wav';
    } else if (ext === '.mp3') {
      contentType = 'audio/mpeg';
    }

    // 返回音频文件
    return new NextResponse(fileBuffer, {
      status: 200,
      headers: {
        'Content-Type': contentType,
        'Content-Length': stats.size.toString(),
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    });
  } catch (error: any) {
    console.error('Error serving audio file:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

