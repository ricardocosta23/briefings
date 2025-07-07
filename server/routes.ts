import type { Express, Request, Response } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import multer from "multer";
import { insertFileSchema } from "@shared/schema";
import { z } from "zod";

interface MulterRequest extends Request {
  file?: Express.Multer.File;
}

// Configure multer for memory storage (store files in memory instead of disk)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req: Request, file: Express.Multer.File, cb: multer.FileFilterCallback) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'));
    }
  },
});

export async function registerRoutes(app: Express): Promise<Server> {
  // Get all uploaded files
  app.get("/api/files", async (req, res) => {
    try {
      const files = await storage.getFiles();
      res.json(files);
    } catch (error) {
      res.status(500).json({ message: "Failed to retrieve files" });
    }
  });

  // Upload a new file
  app.post("/api/files/upload", upload.single('file'), async (req: MulterRequest, res: Response) => {
    try {
      if (!req.file) {
        return res.status(400).json({ message: "No file uploaded" });
      }

      // Convert file buffer to base64 for database storage
      const fileBase64 = req.file.buffer.toString('base64');
      
      // Create sanitized filename
      const sanitizedName = req.file.originalname.replace(/[^a-zA-Z0-9.-]/g, '_');
      const uniqueFileName = Date.now() + '_' + sanitizedName;

      const fileData = {
        originalName: req.file.originalname,
        fileName: uniqueFileName,
        filePath: `/api/files/view/${uniqueFileName}`, // Virtual path for database storage
        fileSize: req.file.size,
        mimeType: req.file.mimetype,
        fileData: fileBase64, // Store base64 data
      };

      const validatedData = insertFileSchema.parse(fileData);
      const savedFile = await storage.createFile(validatedData);

      res.json({
        ...savedFile,
        url: `/api/files/view/${savedFile.fileName}`,
      });
    } catch (error: unknown) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: "Invalid file data" });
      }
      if (error instanceof multer.MulterError) {
        if (error.code === 'LIMIT_FILE_SIZE') {
          return res.status(400).json({ message: "File size exceeds 10MB limit" });
        }
        return res.status(400).json({ message: error.message });
      }
      res.status(500).json({ message: "Failed to upload file" });
    }
  });

  // Serve PDF files from database
  app.get("/api/files/view/:filename", async (req, res) => {
    try {
      const filename = req.params.filename;
      
      // Find file in storage by filename
      const files = await storage.getFiles();
      const file = files.find(f => f.fileName === filename);

      if (!file || !file.fileData) {
        return res.status(404).json({ message: "File not found" });
      }

      // Convert base64 back to buffer
      const fileBuffer = Buffer.from(file.fileData, 'base64');

      res.setHeader('Content-Type', 'application/pdf');
      res.setHeader('Content-Disposition', 'inline');
      res.setHeader('Content-Length', fileBuffer.length.toString());
      res.send(fileBuffer);
    } catch (error) {
      res.status(500).json({ message: "Failed to serve file" });
    }
  });

  // Delete a file
  app.delete("/api/files/:id", async (req, res) => {
    try {
      const fileId = parseInt(req.params.id);
      const file = await storage.getFile(fileId);

      if (!file) {
        return res.status(404).json({ message: "File not found" });
      }

      // Delete from storage (no physical file to delete since it's stored in database)
      const deleted = await storage.deleteFile(fileId);
      if (deleted) {
        res.json({ message: "File deleted successfully" });
      } else {
        res.status(500).json({ message: "Failed to delete file" });
      }
    } catch (error) {
      res.status(500).json({ message: "Failed to delete file" });
    }
  });

  // Download a file
  app.get("/api/files/download/:filename", async (req, res) => {
    try {
      const filename = req.params.filename;
      
      // Find file in storage by filename
      const files = await storage.getFiles();
      const file = files.find(f => f.fileName === filename);

      if (!file || !file.fileData) {
        return res.status(404).json({ message: "File not found" });
      }

      // Convert base64 back to buffer
      const fileBuffer = Buffer.from(file.fileData, 'base64');

      res.setHeader('Content-Type', 'application/pdf');
      res.setHeader('Content-Disposition', `attachment; filename="${file.originalName}"`);
      res.setHeader('Content-Length', fileBuffer.length.toString());
      res.send(fileBuffer);
    } catch (error) {
      res.status(500).json({ message: "Failed to download file" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
