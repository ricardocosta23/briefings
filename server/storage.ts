import { users, uploadedFiles, type User, type InsertUser, type UploadedFile, type InsertFile } from "@shared/schema";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // File operations
  createFile(file: InsertFile): Promise<UploadedFile>;
  getFiles(): Promise<UploadedFile[]>;
  getFile(id: number): Promise<UploadedFile | undefined>;
  deleteFile(id: number): Promise<boolean>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private files: Map<number, UploadedFile>;
  private currentUserId: number;
  private currentFileId: number;

  constructor() {
    this.users = new Map();
    this.files = new Map();
    this.currentUserId = 1;
    this.currentFileId = 1;
  }

  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentUserId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async createFile(insertFile: InsertFile): Promise<UploadedFile> {
    const id = this.currentFileId++;
    const file: UploadedFile = {
      ...insertFile,
      id,
      uploadTime: new Date(),
      fileData: insertFile.fileData || null,
    };
    this.files.set(id, file);
    return file;
  }

  async getFiles(): Promise<UploadedFile[]> {
    return Array.from(this.files.values()).sort(
      (a, b) => b.uploadTime.getTime() - a.uploadTime.getTime()
    );
  }

  async getFile(id: number): Promise<UploadedFile | undefined> {
    return this.files.get(id);
  }

  async deleteFile(id: number): Promise<boolean> {
    return this.files.delete(id);
  }
}

export const storage = new MemStorage();
