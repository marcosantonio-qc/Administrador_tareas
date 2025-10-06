-- Database and schema initialization for SQL Server
IF DB_ID(N'clubdb') IS NULL
BEGIN
    PRINT 'Database clubdb should be created by container environment.'
END
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = N'dbo')
BEGIN
    EXEC('CREATE SCHEMA dbo');
END
GO

-- Users
IF OBJECT_ID(N'dbo.users', N'U') IS NULL
BEGIN
CREATE TABLE dbo.users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    email NVARCHAR(255) NOT NULL UNIQUE,
    full_name NVARCHAR(255) NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL,
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
END
GO

-- Rooms
IF OBJECT_ID(N'dbo.rooms', N'U') IS NULL
BEGIN
CREATE TABLE dbo.rooms (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(120) NOT NULL UNIQUE,
    location NVARCHAR(255) NULL,
    capacity INT NOT NULL,
    area NVARCHAR(120) NULL,
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
CREATE UNIQUE INDEX ix_rooms_name ON dbo.rooms(name);
END
GO

-- Events
IF OBJECT_ID(N'dbo.events', N'U') IS NULL
BEGIN
CREATE TABLE dbo.events (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    type NVARCHAR(20) NOT NULL,
    organizer NVARCHAR(255) NULL,
    description NVARCHAR(MAX) NULL,
    contact NVARCHAR(255) NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'pending',
    attendees INT NULL,
    room_id INT NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_by_id INT NULL,
    updated_by_id INT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT fk_events_room FOREIGN KEY (room_id) REFERENCES dbo.rooms(id),
    CONSTRAINT fk_events_created_by FOREIGN KEY (created_by_id) REFERENCES dbo.users(id),
    CONSTRAINT fk_events_updated_by FOREIGN KEY (updated_by_id) REFERENCES dbo.users(id),
    CONSTRAINT chk_time_valid CHECK (start_time < end_time)
);
CREATE INDEX ix_events_room_date ON dbo.events(room_id, date);
CREATE UNIQUE INDEX uq_room_date_time_exact ON dbo.events(room_id, date, start_time, end_time);
END
GO

-- Audit Logs
IF OBJECT_ID(N'dbo.audit_logs', N'U') IS NULL
BEGIN
CREATE TABLE dbo.audit_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NULL,
    action NVARCHAR(64) NOT NULL,
    entity NVARCHAR(64) NOT NULL,
    entity_id NVARCHAR(64) NOT NULL,
    detail NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES dbo.users(id)
);
END
GO
